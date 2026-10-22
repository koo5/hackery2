#!/usr/bin/env python3
"""vm_bulk_hold: hold the VMs' bulk transfers paused (or slowed) while this process lives, to free the uplink.

    vm_bulk_hold.py                        # pause until you Ctrl-C
    vm_bulk_hold.py --slow 300             # at most 300 KB/s per transfer instead
    vm_bulk_hold.py -- some-call-app       # only while the command runs; exits with its status

Bulk is what the bench moves in big pieces: a box's result upload into dev44's API (64 MB and up), dev44's
pulls, relays and box seeds. Everything small keeps flowing -- claims, leases, progress, small results, every
page -- so no job is lost or re-solved (hillview recon directions st03; enrich/recon/bulk_dial.py).

Each VM's cpu_shaper serves /bulk beside /cpu. Every --every seconds this votes to each VM with a ttl of --ttl-s,
and on exit (Ctrl-C, SIGTERM, a dropped ssh session, the command ending) it withdraws the vote. Killed outright,
its vote lapses by itself within --ttl-s. A pause takes hold mid-transfer within about a second: a box upload
already arriving trickles on rather than starting over later; a new one is parked on the box and resent after.
"""
import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

# the VMs' cpu_shaper listeners, as vm_cpu_arbiter.service names them
VMS = {"dev4_3": "http://192.168.122.31:18079", "dev44": "http://192.168.122.3:18079"}


def vote(url: str, body: dict) -> str:
    """POST /bulk; -> what the VM says is in force, or why it could not be asked."""
    req = urllib.request.Request(url + "/bulk", data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=3) as r:
            eff = json.load(r)["effective"]
        return "run" if eff["mode"] == "run" else "pause" if eff["mode"] == "pause" else f"slow {eff['kbps']} KB/s"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "NO /bulk (its cpu_shaper predates the bulk dial: restart recon-cpu-shaper there)"
        return f"REFUSED HTTP {e.code}: {e.read()[:200].decode(errors='replace')}"
    except (OSError, ValueError, KeyError) as e:
        return f"UNREACHABLE ({type(e).__name__}: {e})"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--slow", type=int, metavar="KBPS", help="slow bulk to this many KB/s per transfer instead of pausing")
    ap.add_argument("--vm", action="append", metavar="NAME=URL",
                    help=f"a VM's cpu_shaper (repeatable; default: {', '.join(f'{k}={v}' for k, v in VMS.items())})")
    ap.add_argument("--every", type=float, default=10, help="seconds between votes (default 10)")
    ap.add_argument("--ttl-s", type=int, default=30, help="each vote's life: how soon a killed hold lapses (default 30)")
    ap.add_argument("command", nargs="*", help="after --: hold only while this runs")
    a = ap.parse_args()
    if a.slow is not None and a.slow < 1:
        ap.error("--slow must be at least 1 KB/s")
    if not a.every < a.ttl_s:
        ap.error("--every must be shorter than --ttl-s, or the hold lapses between votes")
    vms = dict(v.split("=", 1) for v in a.vm) if a.vm else VMS
    source = f"vm_bulk_hold {os.environ.get('USER', '?')}@{socket.gethostname()} pid {os.getpid()}"
    mode = {"mode": "slow", "kbps": a.slow} if a.slow is not None else {"mode": "pause"}
    hold = {**mode, "source": source, "ttl_s": a.ttl_s}

    said: dict = {}
    def round_(body) -> None:
        for name, url in vms.items():
            got = vote(url, body)
            if said.get(name) != got:
                print(f"vm_bulk_hold: {name}: {got}", file=sys.stderr, flush=True)
                said[name] = got

    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGHUP):
        signal.signal(sig, lambda *_: stop.set())
    child = None
    try:
        round_(hold)
        what = f"slowed to {a.slow} KB/s per transfer" if a.slow is not None else "paused"
        if a.command:
            print(f"vm_bulk_hold: bulk {what} while `{' '.join(a.command)}` runs", file=sys.stderr, flush=True)
            child = subprocess.Popen(a.command)
        else:
            print(f"vm_bulk_hold: bulk {what} (Ctrl-C to release)", file=sys.stderr, flush=True)
        while not stop.wait(a.every):
            if child is not None and child.poll() is not None:
                break
            round_(hold)
    except KeyboardInterrupt:
        pass
    finally:
        said.clear()
        round_({"mode": "run", "source": source, "ttl_s": a.ttl_s})
        print("vm_bulk_hold: released", file=sys.stderr, flush=True)
    return child.wait() if child is not None else 0


if __name__ == "__main__":
    raise SystemExit(main())

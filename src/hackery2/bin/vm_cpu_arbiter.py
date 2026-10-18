#!/usr/bin/env python3
"""vm_cpu_arbiter: keep the VMs' REAL host CPU inside a budget the desktop sets; experiments first, production the rest.

    vm_cpu_arbiter.py --experiments dev4_3=http://192.168.122.31:18079 --production dev44=http://192.168.122.3:18079

The operator, 2026-10-18: one service on the host. The DESKTOP sets the budget -- 100 % of the host's physical cores
when nobody is at it (xprintidle >= --idle-after-s, the luigi_toggler mechanism), --active-budget % (25) when someone
is; no margin (that belongs to the topology). The ARBITER splits it: the experiments VM may use all of it, the
production VM what the experiments VM leaves.

It steers by what the HOST pays, not what a guest reports: the kernel's CPU accounting of the cgroup libvirt gives
each VM (machine.slice/machine-qemu\x2d<id>\x2d<domain>.scope, cpu.stat usage_usec: every thread of the VM, no
process scanning), smoothed over a few seconds -- on 10-18 dev44's guest showed 0.5 cores while its qemu took 2.5. A guest's shaper level does not map to host CPU in
any fixed ratio, so each VM's level is a feedback loop: over its allowance -> level scaled down by allowance/cost,
well under -> raised 10 %. Levels go to each VM's cpu_shaper (hillview enrich/recon/cpu_shaper.py) as source
`host-arbiter`, ttl --ttl-s, so a dead arbiter's caps lift by themselves; the shaper applies the LOWEST live vote.
Logs the budget on every change and each VM's line every --log-every-s.
"""
import argparse
import glob
import json
import logging
import os
import subprocess
import threading
import time
import urllib.request

log = logging.getLogger("vm_cpu_arbiter")


def physical_cores() -> int:
    seen = set()
    for path in glob.glob("/sys/devices/system/cpu/cpu[0-9]*/topology/core_cpus_list"):
        with open(path) as f:
            seen.add(f.read().strip())
    return len(seen) or os.cpu_count() or 1


def idle_ms(display: str) -> int | None:
    try:
        return int(subprocess.check_output(["xprintidle"], env={**os.environ, "DISPLAY": display}, timeout=2))
    except (subprocess.SubprocessError, OSError, ValueError):
        return None


MACHINES = "/sys/fs/cgroup/machine.slice"


def vm_cgroup(domain: str) -> str | None:
    """The VM's cgroup, as libvirt names it (machine-qemu\\x2d<id>\\x2d<escaped domain>.scope); None when it is not
    running. The id changes at every start, so it is looked up every tick; two matches is an error, not a guess."""
    esc = subprocess.check_output(["systemd-escape", domain], text=True).strip()
    found = glob.glob(f"{MACHINES}/machine-qemu\\x2d*\\x2d{glob.escape(esc)}.scope")
    if len(found) > 1:
        raise RuntimeError(f"{domain}: {len(found)} cgroups match: {found}")
    return found[0] if found else None


def cpu_s(cgroup: str) -> float:
    with open(f"{cgroup}/cpu.stat") as f:
        return next(int(line.split()[1]) for line in f if line.startswith("usage_usec ")) / 1e6


class VM:
    def __init__(self, spec: str, role: str):
        name, _, url = spec.partition("=")
        if not name or not url:
            raise SystemExit(f"--{role} wants DOMAIN=SHAPER_URL, not {spec!r}")
        self.name, self.url, self.role = name, url.rstrip("/") + "/cpu", role
        self.level, self.cost, self.allowance = 100.0, 0.0, None
        self.last, self.failing = None, False

    def measure(self, now: float, smooth: float) -> None:
        cg = vm_cgroup(self.name)
        if cg is None:                                            # not running: costs nothing
            self.last, self.cost = None, 0.0
            return
        used = cpu_s(cg)
        if self.last is not None and self.last[2] == cg and now > self.last[0]:   # same VM instance as last tick
            inst = (used - self.last[1]) / (now - self.last[0])
            self.cost += (inst - self.cost) * smooth
        self.last = (now, used, cg)

    def steer(self, allowance: float) -> None:
        self.allowance = allowance
        if self.cost > allowance:
            self.level = max(0.0, self.level * allowance / self.cost) if self.cost > 0 else 0.0
        elif self.cost < 0.85 * allowance:
            self.level = min(100.0, self.level * 1.1 + 1)

    def vote(self, ttl_s: int) -> None:
        level = int(round(self.level / 5) * 5)                    # steps of 5: the shapers re-apply on change only
        body = json.dumps({"level": level, "source": "host-arbiter", "ttl_s": ttl_s}).encode()
        req = urllib.request.Request(self.url, data=body, method="POST", headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=2).read()
            if self.failing:
                log.info("%s answers again", self.url)
            self.failing = False
        except (OSError, ValueError) as e:
            if not self.failing:
                log.warning("%s: %s (quiet until it answers again)", self.url, e)
            self.failing = True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--experiments", action="append", default=[], help="DOMAIN=SHAPER_URL, served first")
    ap.add_argument("--production", action="append", default=[], help="DOMAIN=SHAPER_URL, gets what is left")
    ap.add_argument("--host-cores", type=float, default=None, help="the budget's 100 %% (default: physical cores)")
    ap.add_argument("--active-budget", type=float, default=25, help="%% of the host while someone is at the desktop")
    ap.add_argument("--idle-after-s", type=float, default=120)
    ap.add_argument("--display", default=":0")
    ap.add_argument("--tick-s", type=float, default=1.0)
    ap.add_argument("--smooth", type=float, default=0.4, help="EWMA weight of a tick's CPU reading")
    ap.add_argument("--ttl-s", type=int, default=30)
    ap.add_argument("--log-every-s", type=float, default=60)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cores = a.host_cores or physical_cores()
    exp = [VM(s, "experiments") for s in a.experiments]
    prod = [VM(s, "production") for s in a.production]
    if not exp and not prod:
        raise SystemExit("name at least one --experiments or --production VM")
    log.info("host budget base: %s cores; experiments %s, production %s", cores,
             [v.name for v in exp], [v.name for v in prod])
    present, last_log = None, 0.0
    while True:
        now = time.monotonic()
        ms = idle_ms(a.display)
        now_present = ms is not None and ms < a.idle_after_s * 1000
        budget = cores * (a.active_budget if now_present else 100) / 100
        if now_present != present:
            log.info("desktop %s (idle %s ms): budget %.1f cores", "ACTIVE" if now_present else "idle", ms, budget)
            present = now_present
        for v in exp + prod:
            v.measure(now, a.smooth)
        left = budget
        for v in exp:                                  # experiments first, each up to the whole remaining budget
            v.steer(left)
            left = max(0.0, left - v.cost)
        for v in prod:                                 # production shares what is left
            v.steer(left / len(prod))
        for v in exp + prod:
            threading.Thread(target=v.vote, args=(a.ttl_s,), daemon=True).start()
        if now - last_log >= a.log_every_s:
            log.info("budget %.1f: %s", budget, "; ".join(
                f"{v.name} costs {v.cost:.2f} of {v.allowance:.2f} -> level {round(v.level)}" for v in exp + prod))
            last_log = now
        time.sleep(a.tick_s)


if __name__ == "__main__":
    raise SystemExit(main())

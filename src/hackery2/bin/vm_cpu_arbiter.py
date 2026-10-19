#!/usr/bin/env python3
"""vm_cpu_arbiter: keep the VMs' REAL host CPU inside a budget the desktop sets; experiments first, production the rest.

    vm_cpu_arbiter.py --experiments dev4_3=http://192.168.122.31:18079 --production dev44=http://192.168.122.3:18079

The operator, 2026-10-18: one service on the host. The DESKTOP sets the budget -- 100 % of the host's physical cores
when nobody is at it (xprintidle >= --idle-after-s, the luigi_toggler mechanism), --active-budget % (25) when someone
is; no margin (that belongs to the topology). The ARBITER splits it: the experiments VM may use all of it, the
production VM what the experiments VM leaves.

PRESENT WITHOUT THE DESKTOP (over ssh, where xprintidle sees an idle desktop): `vm_cpu_present.py --budget 25`
connects to --socket (default $XDG_RUNTIME_DIR/vm_cpu_arbiter.sock, mode 600) and holds the connection; while any
such client is connected the budget is the lowest of theirs and the desktop's. When the ssh session drops, the
client dies with it, the kernel closes its end, and the budget returns at the next tick -- nothing to clean up.

It steers by what the HOST pays, not what a guest reports: the kernel's CPU accounting of the cgroup libvirt gives
each VM (machine.slice/machine-qemu\x2d<id>\x2d<domain>.scope, cpu.stat usage_usec: every thread of the VM, no
process scanning), smoothed over a few seconds -- on 10-18 dev44's guest showed 0.5 cores while its qemu took 2.5. A guest's shaper level does not map to host CPU in
any fixed ratio, so each VM's level is a feedback loop: over its allowance -> level scaled down by allowance/cost,
well under -> raised 10 %. Levels go to each VM's cpu_shaper (hillview enrich/recon/cpu_shaper.py) as source
`host-arbiter`, ttl --ttl-s, so a dead arbiter's caps lift by themselves; the shaper applies the LOWEST live vote.
Every vote also carries desktop_idle_s (seconds since the last desktop input, or null when xprintidle fails).
The VM keeps this telemetry in memory for min(ttl_s, 60) seconds and serves GET /desktop-idle.
Logs the budget on every change and each VM's line every --log-every-s.

THE CARD (polaris, the RX 580 that also drives the desktop; STORAGE 2026-10-18, hillview infra/units/host/USAGE-SHAPING.md):
--gpu-shaper-socket PATH (polaris-gpu's control socket, /temp/recon-worker/gpu-shaper.sock as the HOST sees it) gets a
vote every tick as source `desktop`: `offload` while someone is at the desktop, `run` when it is idle, with --ttl-s, so
a dead arbiter's vote lapses and the card goes back to the job (2026-10-19, the operator: "through a socket rather than
the filesystem"; the mode file it replaced was never written -- the host user could not create files in the
container's dir). polaris-gpu takes the most restrictive live vote, so a manual `polaris-gpu set pause` still wins.
No vote while xprintidle fails. Presence clients do not count: an ssh session does not draw on the card. Polaris's
Prometheus reads desktop idleness from the VM's shaper over HTTP and the mode and votes from polaris-gpu itself.
"""
import argparse
import glob
import json
import logging
import os
import socket
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


class Card:
    """polaris-gpu's control socket: one vote a tick as `desktop`; quiet while it does not answer (polaris down)"""

    def __init__(self, path: str):
        self.path, self.failing, self.last = path, False, None

    def vote(self, mode: str, ttl_s: int) -> None:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
                c.settimeout(2)
                c.connect(self.path)
                c.sendall(json.dumps({"vote": mode, "source": "desktop", "ttl_s": ttl_s}).encode() + b"\n")
                ans = json.loads(c.makefile("r").readline() or "null")
            if not isinstance(ans, dict) or "error" in ans:
                raise ValueError(f"answered {ans!r}")
            if self.failing:
                log.info("card: %s answers again", self.path)
            self.failing = False
            if mode != self.last:
                log.info("card: desktop votes %s (in force: %s)", mode, ans.get("mode"))
                self.last = mode
        except (OSError, ValueError) as e:
            if not self.failing:
                log.warning("card: %s: %s (quiet until it answers again)", self.path, e)
            self.failing = True


def cpu_s(cgroup: str) -> float:
    with open(f"{cgroup}/cpu.stat") as f:
        return next(int(line.split()[1]) for line in f if line.startswith("usage_usec ")) / 1e6


class Clients:
    """Connected presence clients: connection -> the budget (%) it asked for. A connection's end is its departure."""
    lock = threading.Lock()
    budgets: dict = {}

    @classmethod
    def lowest(cls) -> float | None:
        with cls.lock:
            return min(cls.budgets.values(), default=None)


def serve(path: str) -> None:
    """Accept presence clients on a unix socket: each sends one line {"budget": 0..100, "who": "..."} and stays."""
    if os.path.exists(path):
        os.unlink(path)                                    # a previous arbiter's socket; only one listens here
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    old = os.umask(0o177)
    srv.bind(path)
    os.umask(old)
    srv.listen()

    def hold(conn):
        key = id(conn)
        try:
            line = conn.makefile("r").readline()
            msg = json.loads(line)
            budget = float(msg["budget"])
            if not 0 <= budget <= 100:
                raise ValueError(f"budget must be 0..100, not {budget}")
        except (ValueError, KeyError, TypeError, OSError) as e:
            conn.sendall(json.dumps({"error": f"{type(e).__name__}: {e}"}).encode() + b"\n")
            conn.close()
            return
        with Clients.lock:
            Clients.budgets[key] = budget
        log.info("present: %s holds the budget at %s %% (%d connected)", msg.get("who", "?"), budget,
                 len(Clients.budgets))
        conn.sendall(json.dumps({"ok": True, "budget": budget}).encode() + b"\n")
        try:
            while conn.recv(4096):                         # a client sends nothing more; EOF = it is gone
                pass
        except OSError:
            pass
        with Clients.lock:
            Clients.budgets.pop(key, None)
        log.info("gone: %s (%d connected)", msg.get("who", "?"), len(Clients.budgets))
        conn.close()

    while True:
        conn, _ = srv.accept()
        threading.Thread(target=hold, args=(conn,), daemon=True).start()


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

    def vote(self, ttl_s: int, desktop_idle_s: float | None) -> None:
        level = int(round(self.level / 5) * 5)                    # steps of 5: the shapers re-apply on change only
        body = json.dumps({"level": level, "source": "host-arbiter", "ttl_s": ttl_s,
                           "desktop_idle_s": desktop_idle_s}).encode()
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
    ap.add_argument("--socket", default=os.path.join(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}",
                                                     "vm_cpu_arbiter.sock"),
                    help="where presence clients (vm_cpu_present.py) connect")
    ap.add_argument("--tick-s", type=float, default=1.0)
    ap.add_argument("--smooth", type=float, default=0.4, help="EWMA weight of a tick's CPU reading")
    ap.add_argument("--ttl-s", type=int, default=30)
    ap.add_argument("--log-every-s", type=float, default=60)
    ap.add_argument("--gpu-shaper-socket", default=None,
                    help="polaris-gpu's control socket as the host sees it: votes `offload` at the desk, `run` when idle")
    a = ap.parse_args()
    if a.gpu_shaper_socket and not os.path.isdir(os.path.dirname(a.gpu_shaper_socket) or "."):
        raise SystemExit(f"{a.gpu_shaper_socket}: its directory does not exist (polaris's /temp/recon-worker, as the host sees it)")
    card = Card(a.gpu_shaper_socket) if a.gpu_shaper_socket else None
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cores = a.host_cores or physical_cores()
    exp = [VM(s, "experiments") for s in a.experiments]
    prod = [VM(s, "production") for s in a.production]
    if not exp and not prod:
        raise SystemExit("name at least one --experiments or --production VM")
    log.info("host budget base: %s cores; experiments %s, production %s", cores,
             [v.name for v in exp], [v.name for v in prod])
    threading.Thread(target=serve, args=(a.socket,), daemon=True, name="presence").start()
    present, last_log = None, 0.0
    while True:
        now = time.monotonic()
        ms = idle_ms(a.display)
        at_desk = ms is not None and ms < a.idle_after_s * 1000
        if card is not None and ms is not None:
            threading.Thread(target=card.vote, args=("offload" if at_desk else "run", a.ttl_s), daemon=True).start()
        held = Clients.lowest()
        pct = min(a.active_budget if at_desk else 100, 100 if held is None else held)
        budget = cores * pct / 100
        state = (at_desk, held)
        if state != present:
            log.info("desktop %s (idle %s ms), clients' lowest %s: budget %.1f cores (%g %%)",
                     "ACTIVE" if at_desk else "idle", ms, held, budget, pct)
            present = state
        for v in exp + prod:
            v.measure(now, a.smooth)
        left = budget
        for v in exp:                                  # experiments first, each up to the whole remaining budget
            v.steer(left)
            left = max(0.0, left - v.cost)
        for v in prod:                                 # production shares what is left
            v.steer(left / len(prod))
        for v in exp + prod:
            threading.Thread(target=v.vote, args=(a.ttl_s, None if ms is None else ms / 1000), daemon=True).start()
        if now - last_log >= a.log_every_s:
            log.info("budget %.1f: %s", budget, "; ".join(
                f"{v.name} costs {v.cost:.2f} of {v.allowance:.2f} -> level {round(v.level)}" for v in exp + prod))
            last_log = now
        time.sleep(a.tick_s)


if __name__ == "__main__":
    raise SystemExit(main())

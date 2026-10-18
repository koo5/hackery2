#!/usr/bin/env python3
"""vm_cpu_present: hold the VMs' host-CPU budget down while this process lives (for an ssh session).

    vm_cpu_present.py                      # 25 % of the host until you Ctrl-C or the ssh session drops
    vm_cpu_present.py --budget 10          # any 0..100
    vm_cpu_present.py -- make -j8          # only while the command runs; exits with its status

It connects to vm_cpu_arbiter's socket, says the budget it wants, and keeps the connection open: the arbiter
counts it present until the connection ends. Nothing to undo -- when the ssh session drops, sshd hangs up this
process, the kernel closes the socket, and the arbiter raises the budget at its next tick. (Inside tmux or screen
it survives the drop, by design of those: run it outside them, or with `-- <command>`.)
"""
import argparse
import json
import os
import socket
import subprocess
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--budget", type=float, default=25, help="%% of the host's cores the VMs may use (default 25)")
    ap.add_argument("--socket", default=os.path.join(os.environ.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}",
                                                     "vm_cpu_arbiter.sock"))
    ap.add_argument("command", nargs="*", help="after --: hold the budget only while this runs")
    a = ap.parse_args()
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(a.socket)
    except OSError as e:
        print(f"vm_cpu_present: cannot reach the arbiter at {a.socket}: {e}", file=sys.stderr)
        return 1
    who = f"{os.environ.get('USER', '?')}@{os.environ.get('SSH_CONNECTION', 'local').split(' ')[0]} pid {os.getpid()}"
    s.sendall(json.dumps({"budget": a.budget, "who": who}).encode() + b"\n")
    reply = json.loads(s.makefile("r").readline() or "{}")
    if not reply.get("ok"):
        print(f"vm_cpu_present: refused: {reply}", file=sys.stderr)
        return 1
    print(f"vm_cpu_present: holding the VMs at {reply['budget']} % of the host"
          + (f" while `{' '.join(a.command)}` runs" if a.command else " (Ctrl-C to release)"), file=sys.stderr)
    if a.command:
        return subprocess.call(a.command)
    try:
        s.recv(1)                                        # blocks until the arbiter goes away or we are killed
        print("vm_cpu_present: the arbiter closed the connection", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Alerts that background jobs raise for a human, shared across machines.

A job that hits a condition someone needs to see about writes
<root>/<host>/alerts/<name>.alert. The tree is synced, so an alert raised on
t14 is visible from jj, and because each host owns its own directory there is
nothing for two machines to conflict over.

Two write styles coexist deliberately:

  raise_alert()   overwrites, and the producer clear_alert()s it once the
                  condition resolves -- for self-healing stalls, e.g. a job
                  waiting for an ssh-agent to be unlocked.
  append_alert()  adds a timestamped line and never truncates -- for a
                  permanent record that something may have been lost, e.g. an
                  SD card copy that aborted partway. Clear these by hand, once
                  they have actually been acted on.

Deliberately stdlib-only, so consumers can use it without hackery2 installed:

    sys.path.insert(0, "/home/koom/hackery2/src")
    from hackery2.lib import alert

and from shell, where importing is not an option:

    python3 /home/koom/hackery2/src/hackery2/lib/alert.py append foo "it broke"
"""

import os
import socket
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(os.environ.get("ALERTS_ROOT", "/d/sync/jj/host"))
HOST = socket.gethostname().split(".")[0]

USAGE = """usage: alert <command> [args]

  dir                      print this host's alert directory
  path <name>              print the path of this host's <name> alert
  raise <name> <text...>   overwrite <name> (for self-healing conditions)
  append <name> <text...>  add a timestamped line to <name>, never truncating
  clear <name>             remove this host's <name> alert
  list                     list every alert on every synced host
"""


def alert_dir(host=None, create=True):
    """This host's alert directory (another host's, if given)."""
    d = ROOT / (host or HOST) / "alerts"
    if create:
        d.mkdir(parents=True, exist_ok=True)
    return d


def alert_path(name, host=None, create=True):
    return alert_dir(host, create) / f"{name}.alert"


def raise_alert(name, text):
    """Overwrite <name>. Unchanged text is left alone, so the mtime only moves
    when the message actually changes and syncing stays quiet."""
    path = alert_path(name)
    text = text.rstrip() + "\n"
    if path.exists() and path.read_text() == text:
        return path
    path.write_text(text)
    return path


def append_alert(name, line):
    """Add one timestamped line, keeping everything already recorded."""
    path = alert_path(name)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with path.open("a") as f:
        f.write(f"[{stamp}] {line.rstrip()}\n")
    return path


def clear_alert(name, host=None):
    alert_path(name, host, create=False).unlink(missing_ok=True)


def list_alerts():
    """(host, name, path) for every alert on every synced machine."""
    found = []
    for d in sorted(ROOT.glob("*/alerts")):
        for path in sorted(d.glob("*.alert")):
            found.append((d.parent.name, path.stem, path))
    return found


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "list"
    rest = args[1:]
    try:
        if cmd == "dir":
            print(alert_dir())
        elif cmd == "path":
            print(alert_path(rest[0]))
        elif cmd == "raise":
            print(raise_alert(rest[0], " ".join(rest[1:])))
        elif cmd == "append":
            print(append_alert(rest[0], " ".join(rest[1:])))
        elif cmd == "clear":
            clear_alert(rest[0])
        elif cmd == "list":
            for host, name, path in list_alerts():
                print(f"{host}\t{name}\t{path}")
        else:
            sys.stderr.write(USAGE)
            return 2
    except IndexError:
        sys.stderr.write(USAGE)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

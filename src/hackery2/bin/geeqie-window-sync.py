#!/usr/bin/env python3
"""
Mirror the file shown in the primary Geeqie window into a second window
in the same Geeqie process.

Uses Geeqie's --id=<window-id> mechanism (GTK4-era). Both windows live
in one process; there is no longer a "slave instance".
"""

import subprocess
import time


def gg(*args):
    cmd = ["gg"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()


def window_list():
    return gg("--get-window-list").splitlines()


def main():
    before = window_list()
    if not before:
        raise SystemExit("No primary Geeqie window running. Start `gg` first.")
    primary = before[0]

    gg("--new-window")
    # Wait for the new window to register.
    for _ in range(20):
        after = window_list()
        new = [w for w in after if w not in before]
        if new:
            break
        time.sleep(0.1)
    else:
        raise SystemExit("Slave window did not appear.")
    slave = new[0]

    print(f"primary={primary}  slave={slave}")

    last_file = ""
    try:
        while True:
            current_file = gg(f"--id={primary}", "--tell")
            if current_file and current_file != last_file:
                gg(f"--id={slave}", f"--file={current_file}")
                last_file = current_file
            time.sleep(0.1)
    except KeyboardInterrupt:
        gg(f"--id={slave}", "--close-window")
        print("\nStopped.")


if __name__ == "__main__":
    main()

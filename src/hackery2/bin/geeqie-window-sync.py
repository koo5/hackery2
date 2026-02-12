#!/usr/bin/env python3

import subprocess
import time
import os

GEEQIE2_ENV = {
    **os.environ,
    "XDG_CONFIG_HOME": os.path.expanduser("~/.config/geeqie2"),
    "XDG_CACHE_HOME": os.path.expanduser("~/.cache/geeqie2"),
    "XDG_DATA_HOME": os.path.expanduser("~/.local/share/geeqie2"),
}

def geeqie_remote(*args, env=None):
    cmd = ["geeqie", "--remote"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return result.stdout.strip()

def main():
    # Launch second instance with separate XDG dirs
    subprocess.Popen(["geeqie"], env=GEEQIE2_ENV)
    time.sleep(2)

    last_file = ""

    try:
        while True:
            current_file = geeqie_remote("--tell")

            if current_file and current_file != last_file:
                geeqie_remote(f"--file:{current_file}", env=GEEQIE2_ENV)
                last_file = current_file

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
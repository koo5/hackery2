#!/usr/bin/env python3

import subprocess
import time
import json

def run_command(command):
    start_time = time.time()
    subprocess.run(command, shell=True)
    end_time = time.time()
    return end_time - start_time

if __name__ == "__main__":
    command = "/home/koom/sshcmd1.sh"
    execution_time = run_command(command)

    # Outputting the time in JSON format
    print(json.dumps({"runtime": round(execution_time,2)}))

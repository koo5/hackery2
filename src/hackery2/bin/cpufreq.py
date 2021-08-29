#!/usr/bin/env python3
import sys
import time
import shlex
import subprocess
cmd = sys.argv[1:]

for i in range(8):
	cmdlist = shlex.split("cpufreq-set -c " + str(i))
	cmdlist += cmd
	print(shlex.join(cmdlist))
	subprocess.call(cmdlist)
	time.sleep(0.1)


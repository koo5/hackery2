#!/usr/bin/env python3
import os
import sys
import time
import shlex
import subprocess
cmd = sys.argv[2:]

for i in range(int(sys.argv[1])):
	cmdlist = shlex.split("cpufreq-set -c " + str(i))
	cmdlist += cmd
	print(shlex.join(cmdlist))
	subprocess.call(cmdlist)
	#	time.sleep(int(os.environ['DELAY']))


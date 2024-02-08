#!/usr/bin/env python3
import subprocess, shlex, os


process = subprocess.Popen(shlex.split('journalctl -f /usr/lib/systemd/systemd-logind -n 0'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
for line in process.stdout:
	#print(line.__repr__())
	line = line.strip()
	if line.endswith('Power key pressed.'):
		print('sleep.')
		os.system('/home/koom/hackery2/src/hackery2/bin/sleep.sh')

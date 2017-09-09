#!/usr/bin/env python3
import sys
import time
import subprocess
while True:
	for i in 'abcde':
		hdd = "/dev/sd" + i
		print(subprocess.call("hdparm -C "+hdd + ";hdparm -y " + hdd + ";hdparm -C "+hdd, shell = True))
	time.sleep(1)

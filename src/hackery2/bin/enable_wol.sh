#!/usr/bin/env python3

import os, subprocess, shlex, time


os.system('ethtool -s enp5s0 wol g')
os.system('ethtool -s enx00e081391d14 wol g')

while True:

	try:
		subprocess.check_call(shlex.split('ping -qq -c 1 8.8.8.8'))
	except:
		os.system('nmcli c down ppp')
		time.sleep(5)
		os.system('nmcli c up ppp')

	print('sleep....')
	time.sleep(60)

#!/usr/bin/env python3

import subprocess, shlex, os
import sys


def find_firefox_source1():
	f = subprocess.check_output(['/usr/bin/which', 'firefox'], text=True)

	if f.startswith('/usr/bin/'):
		with open('/usr/bin/firefox') as ff:
			if '/snap/bin/firefox' in ff.read(200):
				print('firefox is from snap')
				return 'snap'

		print('firefox is from apt')
		return 'apt'
	else:
		print('firefox is from snap, i think')
		return 'snap'


def find_firefox_source2():
	f = subprocess.check_output(['firefox', '--help'], text=True)
	if '/snap/' in f:
		print('firefox is from snap')
		return 'snap'
	else:
		print('firefox is from apt')
		return 'apt'

ff1 = find_firefox_source1()
ff2 = find_firefox_source2()
if ff1 != ff2:
	print("i'm confused")
	sys.exit(1)



if ff1 == 'apt':
	subprocess.check_call(['security_updates.sh'])
else:
	subprocess.check_call(shlex.split('sudo snap refresh firefox'))

os.system('firefox')


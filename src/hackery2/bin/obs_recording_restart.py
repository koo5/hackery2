#!/usr/bin/env python3


import subprocess,shlex,time

def co(x):
	print('cmd:'+x)
	r = subprocess.check_output(shlex.split(x), text=True)
	print('result:'+r)
	if r != '':
		r = r.splitlines()[0]
	time.sleep(0.25)
	return r


if co('obs-cli --password ccfa0506 recording status') != 'Recording: true':
	exit()
co('obs-cli --password ccfa0506 recording stop')

#co('xcalib -a -i')
co('/home/koom/xrandr-invert-colors/xrandr-invert-colors.bin -s 0')

while True:
	if co('obs-cli --password ccfa0506 recording status') == 'Recording: false':
		break

#co('xcalib -a -i')
co('/home/koom/xrandr-invert-colors/xrandr-invert-colors.bin -s 0')

co('obs-cli --password ccfa0506 recording start')

#while True:
#	if co('obs-cli --password ccfa0506 recording status') == 'Recording: true':
#		break



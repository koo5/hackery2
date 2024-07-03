#!/usr/bin/env python3
import sys,os

ll = '#'.encode('utf-8')

tty = os.environ.get('USB', '/dev/ttyUSB0')

import os

if not os.path.exists(tty):
	tty = '/dev/ttyUSB1'

if not os.path.exists(tty):
	tty = '/dev/ttyUSB2'

# set baud rate
os.system('stty -F ' + tty + ' 115200')

with open(tty, 'rb') as f:
	
	legend = None

	while True:
	
	
		l = f.readline()

		sys.stderr.write(str(l))
		sys.stderr.write('\n')
		
		if len(l) == 0:
			continue

		if len(l) > 2 and l[0] == 35 and l[1] == 35: 
			print(l.decode('utf-8').strip().rstrip(',')[1:])
			legend = True

		elif l[0] == 33:
			continue

		elif legend != None:
			break
	
	
	while True:
		l = f.readline()
		
		if l[0] == 33:
			continue
		#print('>>>')
		print(l.decode('utf-8').strip().rstrip(','))
		
				
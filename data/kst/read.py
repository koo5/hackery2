#!/usr/bin/env python3
import sys

ll = '#'.encode('utf-8')


with open('/dev/ttyUSB0', 'rb') as f:
	
	legend = None

	while True:
	
	
		l = f.readline()

		#print(l)
		
		if len(l) == 0:
			continue

		if l[0] == 35:
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
		
				
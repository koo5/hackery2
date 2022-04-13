#!/usr/bin/env python3


import os,time,datetime
while True:
	print('=======================')
	print(datetime.datetime.now())
	print('=======================')
	for x in 'psb':
		os.system('xsel -t 100 -n -o -' + x) 
		print()
	print()
	time.sleep(0.5)

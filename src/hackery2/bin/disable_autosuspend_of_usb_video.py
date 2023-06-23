#!/usr/bin/env python3


import os,time,datetime,subprocess,shlex,glob,pathlib




def toggle(f):
	f = pathlib.Path(f + '/../power/control').resolve(strict=False)
	print(str(f) + ' << on')
	open(f,'w').write('on')
	print()




for f in glob.glob('/sys/bus/usb/devices/*/*'):
	try:
		maybe_interface_file = f + '/interface'

		with open(maybe_interface_file) as i:
			contents = i.readlines()[0]
			#print(maybe_interface_file)
			#print(contents.__repr__())
			if contents == 'USB Video\n':
				#print('toggle')
				toggle(f)
	except (NotADirectoryError, FileNotFoundError) as e:
		#print(e.__repr__())
		pass

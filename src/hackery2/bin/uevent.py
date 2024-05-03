#!/usr/bin/env python3


import os,time,datetime,subprocess,shlex,glob,pathlib,sys,click,re


@click.command()
#@click.argument('new_state', type=str, 	default='0')
def x():
	#
	r = re.compile('.*/video4linux/video.*/device')

	for f in pathlib.Path('/sys/devices/').rglob('*'):
		#print(f)
		if r.match(str(f)):
			print(f)
			#break
			
			f = f / 'uevent'
			try:
				with open(f) as i:
					contents = i.readlines()
					print(contents.__repr__())
					#open(f,'w').write(new_state)

			except (NotADirectoryError, FileNotFoundError) as e:
				print(e.__repr__())
				pass
	

if __name__ == '__main__':
	x()

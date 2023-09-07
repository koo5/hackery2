#!/usr/bin/env python3


import os,time,datetime,subprocess,shlex,glob,pathlib,sys,click




def toggle(f,new_state):
	f = pathlib.Path(f + '/../power/control').resolve(strict=False)
	print(str(f) + ' << ' + new_state)
	open(f,'w').write(new_state)
	print()


@click.command()
@click.argument('new_state', type=str, 	default='on')
def x(new_state):

	for f in glob.glob('/sys/bus/usb/devices/*/*'):
		try:
			maybe_interface_file = f + '/interface'

			with open(maybe_interface_file) as i:
				contents = i.readlines()[0]
				#print(maybe_interface_file)
				#print(contents.__repr__())
				if contents == 'USB Video\n':
					#print('toggle')
					toggle(f,new_state)
		except (NotADirectoryError, FileNotFoundError) as e:
			#print(e.__repr__())
			pass



if __name__ == '__main__':
	x()

#!/usr/bin/env python3


import os,time,datetime,subprocess,shlex,glob,pathlib,sys,click


@click.command()
@click.argument('new_state', type=str, 	default='0')
def x(new_state):
	print(new_state)

	for f in pathlib.Path('/sys/devices/').rglob('pm_qos_no_power_off'):
		print(f)

		try:
			with open(f) as i:
				contents = i.readlines()[0]
				print(contents.__repr__())
				open(f,'w').write(new_state)

		except (NotADirectoryError, FileNotFoundError) as e:
			#print(e.__repr__())
			pass


if __name__ == '__main__':
	x()

#!/usr/bin/env python3
import sys,os
import time
import subprocess
import click

@click.command()
@click.option('--keep_putting_to_sleep', type=bool, default=False)
def main(keep_putting_to_sleep):
	while True:
		for i in 'abcde':
			hdd = "/dev/sd" + i
			print(hdd)
			if not os.path.exists(hdd):
				continue

			print(subprocess.call("hdparm -C "+hdd, shell = True))
			if keep_putting_to_sleep:
				print(subprocess.call("hdparm -y " + hdd, shell = True))
				print(subprocess.call("hdparm -C "+hdd, shell = True))
	
			time.sleep(1)
if __name__ == '__main__':
	main()
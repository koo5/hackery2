#!/usr/bin/env python3

import os
import sys
import click 


@click.command()
@click.argument('dir', type=click.Path(exists=True))
@click.argument('cmd', default='run')
@click.option('--usb', default='', help='USB device to use')
def run(dir, cmd, usb):

	os.chdir(dir)
	name = dir.strip('/')
	
	if usb == 'auto':
		for tty in ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"]:
			if os.path.exists(tty):
				usb = tty
				break
	
	if usb != '':
		usb = f'--device {usb}'			
	
	cmd = f"docker run --rm --network host -v /var/run/dbus:/var/run/dbus -v (pwd):/config {usb} -it esphome/esphome -s name {name} {cmd} main.yaml {usb}"
	print(cmd)
	os.system(f'fish -c "{cmd}"')
	

if __name__ == '__main__':
	run()
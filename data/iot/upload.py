#!/usr/bin/env python3

import os
import pathlib
import subprocess
import sys
import click
import jinja2


@click.command()
@click.argument('dir', type=click.Path(exists=True))
@click.option('bid', default='0', help='board id, parametrize the config.')
@click.argument('cmd', default='run', help='esphome command override, (run, logs, etc?)')
@click.option('--usb', default='', help='USB device to use (instead of wireless OTA upload to IP address)')
def run(dir, bid, cmd, usb):

	# where to upload

	if usb == 'auto':
		for tty in ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"]:
			if os.path.exists(tty):
				usb = tty
				break
	
	if usb != '':
		usb = f'--device {usb}'			
	
	# what to upload

	os.chdir(dir)
	name = dir.strip('/')
	
	# instantiate templates
	
	instdir = f'inst/{bid}'
	pathlib.mkdir(instdir, parents=True, exist_ok=True)
	
	
	yaml_files = list(pathlib.Path('.').rglob('*.yaml'))
	for yaml_file in yaml_files:
		with open(yaml_file) as f:
			yaml = f.read()
			step = jinja2.Template(yaml, autoescape=False)
			#tmpl = step.Template(TEMPLATE_STRING, strip=False, escape=False)
			yaml = step.render(bid = bid)
		with open(f'{instdir}/{yaml_file}', 'w') as f:
			f.write(yaml)
			subprocess.call(['diff', yaml_file, f'{instdir}/{yaml_file}'])
	
	# upload
	
	os.chdir(instdir)
	
	cmd = f"docker run --rm --network host -v /var/run/dbus:/var/run/dbus -v (pwd):/config {usb} -it esphome/esphome -s name {name} {cmd} main.yaml {usb}"
	print(cmd)
	os.system(f'fish -c "{cmd}"')
	

if __name__ == '__main__':
	run()
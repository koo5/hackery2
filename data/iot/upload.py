#!/usr/bin/env python3

import os
import pathlib
import subprocess
import sys
#import click
#import fire
import typer
import jinja2


# @click.command()
# @click.argument('dir', type=click.Path(exists=True))
# @click.option('bid', default='0', help='board id, parametrize the config.')
# @click.argument('cmd', default='run', help='esphome command override, (run, logs, etc?)')
# @click.option('--usb', default='', help='USB device to use (instead of wireless OTA upload to IP address)')



app = typer.Typer()

@app.command()
def run(dir: pathlib.Path, bid=0, cmd='run', usb=''):

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
	name = str(dir).strip('/')
	
	# instantiate templates
	
	instdir = f'inst/{bid}'
	os.makedirs(instdir, exist_ok=True)	
	
	yaml_files = list(pathlib.Path('.').glob('*.yaml'))
	print(yaml_files)
	for yaml_file in yaml_files:
		with open(yaml_file) as f:
			yaml = f.read()
			step = jinja2.Template(yaml, autoescape=False, keep_trailing_newline=True)
			#tmpl = step.Template(TEMPLATE_STRING, strip=False, escape=False)
			yaml = step.render(dir = name, bid = bid, dirbid = f'{name}{bid}')
		out = f'{instdir}/{yaml_file}'
		with open(out, 'w') as f:
			f.write(yaml)
		subprocess.call(['diff', yaml_file, out])
	
	# upload
	
	os.chdir(instdir)
	
	cmd = f"docker run --rm --network host -v /var/run/dbus:/var/run/dbus -v (pwd):/config {usb} -it esphome/esphome -s name {name} {cmd} main.yaml {usb}"
	print(cmd)
	os.system(f'fish -c "{cmd}"')
	

if __name__ == '__main__':
	#run()
    typer.run(run)
	
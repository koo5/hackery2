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
def run(dir: pathlib.Path, bid=0, cmd='run', device=''):

	# where to upload

	if device == 'auto':
		for tty in ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0"]:
			if os.path.exists(tty):
				device = tty
				break

	usb = ''

	if device != '':
		if device.startswith('/dev/'):
			usb = f'--device {device}'
		device = f'--device {device}'

	# what to upload

	os.chdir(dir)
	name = str(dir).strip('/')
	
	
	# instantiate templates
	
	instdir = pathlib.Path(f'inst/{bid}')
	os.makedirs(instdir, exist_ok=True)	

	config = {}
	config['dir'] = name
	config['bid'] = bid
	config['dirbid'] = f'{name}{bid}'

	config_file = pathlib.Path('config.py')
	if config_file.exists():
		sys.path.append('.')
		import config as config_module
		config = config_module.config(config)

	yaml_files = list(pathlib.Path('.').glob('*.yaml'))
	print(yaml_files)
	for yaml_file in yaml_files:
		with open(yaml_file) as f:
			yaml = f.read()
			step = jinja2.Template(yaml, autoescape=False, keep_trailing_newline=True)
			#tmpl = step.Template(TEMPLATE_STRING, strip=False, escape=False)
			yaml = step.render(**config)
		out = f'{instdir}/{yaml_file}'
		with open(out, 'w') as f:
			f.write(yaml)
		subprocess.call(['diff', yaml_file, out])
		
	
	# reuse previous esphome build dir
		
	if not (instdir / '.esphome').exists():
		if int(bid) > 0:
			subprocess.call(['rsync', '-r', '-a', '-v', 
				'--include', 'platformio',
				'--exclude', '*',
				f'inst/{str(int(bid)-1)}/.esphome/',
				instdir / '.esphome'
			])
	
	
	# upload
	
	os.chdir(instdir)
	
	cmd = f"docker run --rm --network host -v /var/run/dbus:/var/run/dbus -v (pwd):/config {usb} -it esphome/esphome -s name {name} {cmd} main.yaml {device}"
	print(cmd)
	os.system(f'fish -c "{cmd}"')
	

if __name__ == '__main__':
	#run()
    typer.run(run)
	
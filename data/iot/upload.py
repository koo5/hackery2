#!/usr/bin/env python3


#  sudo apt install python3-typer



import json
import os
import pathlib
import shlex
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
def run(dir: pathlib.Path, bid=0, cmd='run', device='', podman='docker'):

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


	os.system(f'{podman} volume create esphome_cache')
	os.system(f'{podman} volume create esphome_build')

	# what to upload

	name = pathlib.Path(str(dir).strip('/'))

	# instantiate templates

	inst = pathlib.Path(bid)
	instdir = pathlib.Path('inst') / name / inst
	build = json.loads(subprocess.check_output(shlex.split(f'{podman} volume inspect esphome_build')))[0]['Mountpoint']
	instpath = build / instdir
	os.makedirs(instpath, exist_ok=True)


	config = {}
	config['dir'] = name # directory of the esphome config
	config['bid'] = bid # board id
	config['dirbid'] = f'{name}{bid}'

	config_file = pathlib.Path(name / 'config.py')
	if config_file.exists():
		sys.path.append(str(name))
		import config as config_module
		config = config_module.config(config)

	yaml_files = list(pathlib.Path('.').glob(str(name) + '/*.yaml'))
	print(yaml_files)
	for yaml_file in yaml_files:
		with open(yaml_file) as f:
			yaml = f.read()
			step = jinja2.Template(yaml, autoescape=False, keep_trailing_newline=True)
			#tmpl = step.Template(TEMPLATE_STRING, strip=False, escape=False)
			yaml = step.render(**config)
		outdir = build / instdir
		out = outdir / pathlib.Path(yaml_file).name
		print(out)
		with open(out, 'w') as f:
			f.write(yaml)
		subprocess.call(['diff', yaml_file, out])

	other_files = list(name.rglob('fonts/*')) + list(name.rglob('*.h'))
	for other_file in other_files:
		print(other_file)
		out = build/instdir/ (other_file.relative_to(name))
		os.makedirs(out.parent, exist_ok=True)
		print(out)
		subprocess.call(['cp', other_file, out])

	# upload
	cmd = f"{podman} run --rm --network host -v /var/run/dbus:/var/run/dbus -v esphome_cache:/cache -v esphome_build:/config {usb} --security-opt label=type:unconfined_t --privileged -it ghcr.io/esphome/esphome -s name {name} {cmd} /config/{instdir}/main.yaml {device}"
	print(cmd)
	os.system(f'{cmd}')
	

if __name__ == '__main__':
	#run()
    typer.run(run)
	
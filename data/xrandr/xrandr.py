#!/usr/bin/env python3

import subprocess, sys
import logging
import shlex

log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

from arandr import *

outputs = parse_arandr_saved_configuration_shell_file(sys.argv[1])

offs = ['DVI-D-0']

for o in outputs:
	if o['output'] in offs:
		log.debug(f'off {o["output"]}')
		o['off'] = True
		

for o in reversed(outputs):
	if o['off']:
		#print(o)
		subprocess.check_call(['xrandr', '--output', o['output'], '--off'])
		outputs.remove(o)

outputs.sort(key=lambda x: x['pos'][1])

log.debug(f'{len(outputs)=}')

for o in outputs:
	del o['off']
	#log.debug(f'{o=}')


for o in reversed(outputs):
	#print()
	
	cmd = ['xrandr', 
			'--output', o['output'],
			'--auto', 
			'--mode', f'{o["mode"][0]}x{o["mode"][1]}',
			'--pos', f'{o["pos"][0]}x{o["pos"][1]}',
			'--rotate', o['rotate']] + (['--primary'] if o['primary'] else [])
	
	cmdstr = shlex.join(cmd)
	#log.debug(f'{cmdstr=}')

	try:
		subprocess.check_call(cmd)
	except subprocess.CalledProcessError:
		log.debug(f'xrandr failed for {o=}')
		log.debug(f'cmdstr: {cmdstr}')
		log.debug(f'')
		subprocess.check_call(['xrandr', '--output', o['output'], '--off'])
		outputs.remove(o)

log.debug(f'{len(outputs)=}')
for o in outputs:
	log.debug(f'{o=}')
	



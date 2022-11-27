#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import argv, stdout
from time import sleep, asctime
from subprocess import check_output
import datetime

t0 = datetime.datetime.utcnow()

lines = check_output(['xrandr']).decode().splitlines()

l0 = lines[0]
if not l0.startswith('Screen 0: '):
	raise Exception('unexpected first line: ' + l0)

lines = lines[1:]


outputs = []


for line in lines:
	words = line.split()
	w1 = words[1]
	if w1 in ('connected','disconnected'):
		print('xxxx' + line)
		outputs.append({'name':words[0], 'connected':w1=='connected'})
		#sleep(1)

print(outputs)

for output in outputs:
	subprocess.check_call(['xrandr', '--output', output['name'], '--off'])

for oo in ['DisplayPort-2','DVI-D-0','DisplayPort-1','HDMI-A-0','DisplayPort-0','DVI-I-1-1']:
	q(?x name oo), q



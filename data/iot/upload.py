#!/usr/bin/env python3

import os
import sys

os.chdir(sys.argv[1])
name = sys.argv[1].strip('/')

try:
	cmd = sys.argv[2]
except:
	cmd = 'run'


for tty in ["/dev/ttyUSB0", "/dev/ttyACM0"]:
	if os.path.exists(tty):
		usb = f'--device {tty}'
		break
else:
	usb = ''

os.system(f'fish -c "docker run --rm --network host -v /var/run/dbus:/var/run/dbus -v (pwd):/config {usb} -it esphome/esphome -s name {name} {cmd} main.yaml {usb}"')

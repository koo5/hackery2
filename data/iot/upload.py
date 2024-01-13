#!/usr/bin/env python3

import os
import sys

os.chdir(sys.argv[1])

tty = "/dev/ttyUSB0"

# check if tty exists
if os.path.exists(tty):
    usb = f'--device {tty}'
else:
    usb = ''

os.system(f'fish -c "docker run --rm --network host -v /var/run/dbus:/var/run/dbus -v (pwd):/config {usb} -it esphome/esphome run main.yaml {usb}"')


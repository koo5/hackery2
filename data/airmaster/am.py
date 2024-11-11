#!/usr/bin/env python3
import glob
import os, sys
import subprocess

usb_dev = os.environ.get('USB_DEV', None)
if usb_dev is None:
    print('USB_DEV not set')
    sys.exit(1)

dev = glob.glob(usb_dev + '/ttyUSB*')
print(dev)
name = dev[0].split('/')[-1]

AM7_PORT = '/dev/' + name

os.chdir(os.path.dirname(os.path.realpath(__file__)))

eee = os.environ.copy()
eee['AM7_PORT'] = AM7_PORT

print('AM7_PORT:', AM7_PORT)

sys.exit(subprocess.run(['./your_program_name'], env=eee).returncode)

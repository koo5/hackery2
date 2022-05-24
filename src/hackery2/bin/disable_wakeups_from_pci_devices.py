#!/usr/bin/env python3


import os,time,datetime,subprocess


def toggle(line):
	print(line)
	open('/proc/acpi/wakeup','w').write(line)
	
for line in open('/proc/acpi/wakeup','r'):
	if 'enabled' in line:
		toggle(line)

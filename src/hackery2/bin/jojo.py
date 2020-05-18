#!/usr/bin/env python3

import subprocess

# as opposed to dmesg -T, this prints real datetimes, not (seconds after boot, excluding sleep time) converted to datetimes

HOW_MANY_BOOTS_BACK = 0

ignored = ['must not be copy-on-write', 'failed to trim', 'is missing']

dir = []


import sys
if len(sys.argv) > 1:
	dir=['-D', sys.argv[1]]


def ignore(ll):
	for ign in ignored:
		if ign.casefold() in ll:
			return True



def print_log(log):
	for l in log.split('\n'):
		ll = l.casefold()
		#if 'btrfs' in ll:
			#if ('warning' in ll) or ('error' in ll):
			#	if ignore(ll):
			#		continue
		#	print(l)
		print(l)



i = 1
while True:
	try:
		c = ['journalctl'] + dir +['-k', '-b', '+'+str(i), '--all']
		sys.stderr.write(' '.join(c) + '\n')
		log = subprocess.check_output(c, universal_newlines=True)
		print_log(log)
	except Exception as e:
		print(e)
		break
	i += 1


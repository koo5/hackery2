#!/usr/bin/env python3

import subprocess

# as opposed to dmesg -T, this prints real datetimes, not (seconds after boot, excluding sleep time) converted to datetimes

HOW_MANY_BOOTS_BACK = 0

ignored = ['must not be copy-on-write', 'failed to trim', 'is missing']


def ignore(ll):
	for ign in ignored:
		if ign.casefold() in ll:
			return True


log = subprocess.check_output(['journalctl', '-k', '-b', '-all'], universal_newlines=True)


for l in log.split('\n'):
	ll = l.casefold()
	if 'btrfs' in ll:
		if ('warning' in ll) or ('error' in ll):
			if ignore(ll):
				continue
			print(l)

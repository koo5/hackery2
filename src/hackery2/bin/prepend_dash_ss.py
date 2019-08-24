#!/usr/bin/env python2

import sys

for i in sys.stdin.readlines():
	sys.stdout.write(' -s ' + i.strip())
	

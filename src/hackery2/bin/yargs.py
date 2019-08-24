#!/usr/bin/env python2

import sys, os

for i in sys.stdin.readlines():
	os.system(sys.argv[1] + ' ' + i)

	

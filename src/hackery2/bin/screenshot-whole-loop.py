#!/usr/bin/env python2.7
import os, time, sys
while True:
	os.system("scrot  -q 80 " +sys.argv[1]+"/$(date +%Y%m%d%H%M%S).png")
	os.system("df -h " + sys.argv[1])
	time.sleep(0.1)


#!/usr/bin/env python3


#this file is cc by-sa 3.0 with attribution required, because it is mostly just bits from SO pasted together

import json
import urllib.request, urllib.parse
import sys, os, time, datetime

def s(x):
	print(x+':')
	os.system(x)
	print()
	

while True:
	print(datetime.datetime.fromtimestamp(time.time()))
	s('xclip -o -selection primary')
	s('xclip -o -selection secondary')
	s('xclip -o -selection clipboard')
	time.sleep(1)
	print()
	print()

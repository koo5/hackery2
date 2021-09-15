#!/usr/bin/env python3
import os, time, sys
while True:
	try:
		os.system('fish -c "env DISPLAY=:0.0 xfwm4 --replace"')
	except:
		pass
	time.sleep(1)

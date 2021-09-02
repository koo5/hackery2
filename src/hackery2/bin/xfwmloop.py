#!/usr/bin/env python3
import os, time, sys
while True:
	os.system('fish -c "env DISPLAY=:0.0 xfwm4 --replace"')
	time.sleep(1)

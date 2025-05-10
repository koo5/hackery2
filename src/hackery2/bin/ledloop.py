#!/usr/bin/env python3
import os, time
for i in range(1,33):
	cmd = "xset  -led " + str(i)
	print(cmd)
	os.system(cmd)
	

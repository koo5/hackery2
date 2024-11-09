#!/usr/bin/env python3


import os,time,datetime,subprocess,glob


for x in glob.glob('/dev/video*'):
	subprocess.Popen(["/usr/bin/guvcview","-d",x])

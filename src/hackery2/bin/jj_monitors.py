#!/usr/bin/env python3


import os,time,datetime,subprocess,glob

for x in """



""".splitlines():
os.system('xrandr ' + x)


'xrandr --output DisplayPort-0 --off --output DisplayPort-1 --off --output DisplayPort-2 --off --output HDMI-A-0 --primary --mode 3840x2160 --pos 1920x1080 --rotate normal --output DVI-D-0 --mode 1920x1080 --pos 0x0 --rotate normal --output DVI-I-4-4 --off --output DVI-I-3-3 --off --output DVI-I-2-2 --off --output DVI-I-1-1 --mode 1280x1024 --pos 5760x3240 --rotate normal



a bit of a problem is that we can't detect if a tv is switched on or off
i guess the only solution is to hack arandr to:
	1) write proper settings scriipts :)
	2) periodically write current configured configuration to a file somewhere, where a periodic script can grab it, in a declarative way,

	iiidk

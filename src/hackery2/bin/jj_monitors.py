#!/usr/bin/env python3


import os


os.system('/home/koom/hackery2/data/xrandr/xrandr.py ~/.screenlayout/fff.sh')



# 
# a bit of a problem is that we can't detect if a tv is switched on or off
# i guess the only solution is to hack arandr to:
# 	1) write proper settings scriipts :)
# 	2) periodically write current configured configuration to a file somewhere, where a periodic script can grab it, in a declarative way,
# 
# 	iiidk

#!/usr/bin/env python3

# sudo apt install python3-xlib

from Xlib import X, display
from Xlib.ext import randr

d = display.Display()
s = d.screen()
window = s.root.create_window(0, 0, 1, 1, 1, s.root_depth)

res = randr.get_screen_resources(window)
#import IPython; IPython.embed()

randr.set_screen_size()

for mode in res.modes:
    w, h = mode.width, mode.height
    print ("Width: {}, height: {}".format(w, h))
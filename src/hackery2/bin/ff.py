#!/usr/bin/env python3

import os, sys, subprocess

# todo: magically check that the profile is not in use on another machine. maybe also have a heuristick with file timestamps.

sys.exit(subprocess.call(['firefox'] + sys.argv[1:]))

# xdg-settings set default-web-browser ff.desktop



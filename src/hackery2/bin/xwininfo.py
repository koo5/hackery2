#!/usr/bin/env python3
import subprocess, shlex
print()
print()

#r = (subprocess.check_output(['fish', '-c'] + shlex.split("xwininfo 2>&1 | grep 'Window id:' | sed 's/xwininfo: Window id: \\(.*\\) \".*/\\1/'  ")))
r = (subprocess.check_output(['fish', '-c'] + shlex.split("xwininfo | grep 'Window id:'  ")))

print()
print()

print(r)

print()
print()
#os.system("scrot  -q 80 ~/screenshots/$(date +%Y%m%d%H%M%S).png")

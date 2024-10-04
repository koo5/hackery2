#!/usr/bin/env python3
import subprocess
import os
import time

os.system("hdparm -B 127 /dev/sda")
os.system("hdparm -B 127 /dev/sdb")
os.system("hdparm -B 127 /dev/sdc")
os.system("hdparm -B 127 /dev/sdd")
os.system("hdparm -B 127 /dev/sde")

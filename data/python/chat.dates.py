#!/usr/bin/env python3

import sys
import datetime


def parse_date(line):
"""
editable-log, chat datetime format
https://www.journaldev.com/23365/python-string-to-datetime-strptime
"""
    l=line[:17]
#   print(l)
    return datetime.datetime.strptime(l, "%d.%m.%y %H:%M:%S")


last_t = None
for line in sys.stdin.readlines():
    if "stoopkid" in line:
        t = None
        try:
            t = parse_date(line)
            #print(t)
        except:
            pass
        if "*** Quit: " in line:
            if last_t != None:
                if t != None:
                    print (t - last_t)
        if t:
            last_t = t



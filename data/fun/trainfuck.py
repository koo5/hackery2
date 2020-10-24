#!/usr/bin/env python
# -*- coding: utf-8 -*-
#for some reason the values in table are all weird for me

import sys

if len(sys.argv) != 2:
	inp = """++++++++++
>>+<<[->[->+>+<<]>[-<+>]>[-<+>]<<<]
"""
else:
	inp = open(sys.argv[1], "r").read()

table = {
'+':u'🚂 ',
'-':u'🚃 ',
'>':u'🚅 ',
'<':u'🚄 ',
'[':u'🚈 ',
']':u'🚉 '}

for i in inp:
	if i in table:
		sys.stdout.write(table[i][0])
print ""

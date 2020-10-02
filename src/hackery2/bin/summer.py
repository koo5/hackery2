#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
simple text terminal summing "calculator"
paste/type in some numbers, only one number per line, with no surrounding text, at most one blank line between them
non-number lines are ignored
two blank lines trigger printing out the sum
"""


import sys

sum = 0

# require two empty lines to trigger computation, accept one empty line as part of input
was_newline = False

for l in sys.stdin:
	if l == '\n':
		if was_newline:
			print('===')
			print(sum)
			sum = 0
		else:
			was_newline = True
	else:
		was_newline = False
		i = l.strip()
		if i != '':
			try:
				i = int(i)
			except:
				continue
			sum = i + sum

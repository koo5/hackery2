#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys

def run():
	if len(sys.argv) == 1:
		for module in modules:
			module.print_functionality()
	input = sys.argv[1]
	print(input)

if __name__ == '__main__':
    sys.exit(run())

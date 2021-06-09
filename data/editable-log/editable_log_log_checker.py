#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
check that "*.log.txt?*" files are fully contained within the main files
"""


from glob import glob

def diff():
	for i in glob('*.log.txt'):
		print (i)
		for j in glob(i + '?*'):
			print(open(j).read() in open(i).read())
		

if __name__ == '__main__':
	diff()

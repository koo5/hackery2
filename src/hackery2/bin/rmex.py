#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pipes

def isonext(path):
	return path.startswith("maglajz")


dupes = []
for l in open("indupes"):
	l = l[:-1]
	if l == "":
		itsonint = False
		for dupe in dupes:
			if not isonext(dupe):
				itsonint = True
				break
		if itsonint:
			for dupe in dupes:
				if isonext(dupe):
					print ("rm " + pipes.quote(dupe))
		dupes = []
	else:
		dupes.append(l)
		

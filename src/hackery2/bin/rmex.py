#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import pipes

def isonext(path):
	return path.startswith("/var/run/media/koom/77df2401-2245-43d9-bb5c-089df9b12177/")


dupes = []
for l in open("dupes"):
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
		

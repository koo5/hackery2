#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def annagram(x, y):
	for letter in x:
		#print ('testing for ',letter)
		if len(y) == 0:	return False
		y = y[0:y.find(letter)] + y[y.find(letter)+1:]
		#print ('y is now ',y)
	if len(y) == 0: return True



assert (annagram("dog", "god"))
assert (not annagram("dog", "good"))
assert (not annagram("dogg", "good"))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def a():
	x = 0
	def b():
		nonlocal x
		x+=1
		print(x)
	return b

b = a()
b()
b()
b()


#!/usr/bin/env python3
import traceback


try:
	a = dict(a1=1)[2]
except Exception as e:
	print('=====')

 	print(str(e))

	print('=====')

	print(repr(e))

	print('=====')

	error_message = traceback.format_exc()
	print(error_message)

	print('=====')

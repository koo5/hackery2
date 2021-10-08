#!/usr/bin/env python3

import os


def delete_snapshots(config='root', where = '/'):
	try:
		for x in os.listdir(where + '/.snapshots'):
			os.system('snapper -c '+config+ ' delete '+x)
	except Exception as e:
		print(e)


delete_snapshots('root', '/')
delete_snapshots('home', '/home/')
delete_snapshots('data', '/d/')
delete_snapshots('c1', '/mx500data/')

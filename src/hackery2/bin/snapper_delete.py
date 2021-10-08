#!/usr/bin/env python3

import os


def delete_snapshots(config='root', where = '/'):
	for x in os.listdir(where + '/.snapshots'):
		os.system('snapper -c '+config+ ' delete '+x)


delete_snapshots('root', '/')
delete_snapshots('home', '/home/')
delete_snapshots('data', '/d/')

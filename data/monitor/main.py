#!/usr/bin/env python3

import sys,os,time
import subprocess
import re
import time
from pathlib import Path

import pygame

pygame.init()


def create_window():

	# create an empty window
	pygame.display.set_mode((1000, 600))
	pygame.display.set_caption('KOOMVCR')
	pygame.display.flip()
	

	# get the window id
	time.sleep(1)
	window_id = subprocess.check_output(['xwininfo', '-name', 'KOOMVCR']).decode()
	window_id = re.search('Window id: (0x[0-9a-f]+)', window_id).group(1)

	print(f'Window id: {window_id}')

	return window_id
	
	
w = create_window()

seen = []

def print_hi(name):
	rootdirs = sys.argv[1:]
	allfiles = {}
	
	while True:
	
		print('list dirs and files...')
		for dir in rootdirs:
			print(dir)
			for root, dirs, files in os.walk(dir):
				print('root, dirs, files: ' + str(root) + ' ' + str(dirs) + ' ' + str(files))
				for file in files:
					print('lll file: ' + str(file))
					f = Path(os.path.join(root, file))
					if f.is_file():
						if f not in allfiles:
							print('found new file: ' + str(f))
							allfiles[str(f)] = f.stat().st_ctime
		
		print('sort by ctime...')
		#allfiles.sort(key=lambda python_sucks: python_sucks[0])
		allfiles = dict(sorted(allfiles.items(), key=lambda item: item[1]))
		
		
		print('play..')
		
		for f in list(allfiles.keys())[-1:]:
			if f not in seen:
				seen.append(f)
				print(f)
				print()
				print()
			# 	
			# 	print(f'File: {f}')				
				print(f'File: {f}')				
				cmd = f'MPLAYER_VERBOSE=-1 mplayer -msglevel all=0 -noautosub -wid {w} "{f}"'
				print(cmd)
				os.system(cmd)

		time.sleep(0.1)
		print('---')
	

if __name__ == '__main__':
	print_hi('PyCharm')

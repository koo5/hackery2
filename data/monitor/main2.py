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
	pygame.display.set_caption('Mousepad')
	pygame.display.flip()
	

	# get the window id
	time.sleep(1)
	window_id = subprocess.check_output(['xwininfo', '-name', 'Mousepad']).decode()
	window_id = re.search('Window id: (0x[0-9a-f]+)', window_id).group(1)

	print(f'Window id: {window_id}')
	print(f'Window id: {window_id}')
	print(f'Window id: {window_id}')

	return window_id
	
	
w = ''#create_window()

seen = []

def print_hi(name):
	dirs = sys.argv[1:]
	
	while True:
		for dir in dirs:
			for root, dirs, files in os.walk(dir):
				for file in files:
					f = os.path.join(root, file)
					if f not in seen and Path(f).is_file():
					
						print(f'File: {f}')
						
						cmd = f'mplayer -wid {w} "{f}"'
						print(cmd)
						
						#os.system(cmd)
						
						seen.append(f)

		#time.sleep(1)
		print('---')
	

if __name__ == '__main__':
	print_hi('PyCharm')

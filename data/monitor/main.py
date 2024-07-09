#!/usr/bin/env python3

import sys,os,time
import subprocess
import re
import time, json, subprocess
from pathlib import Path

import pygame
import requests

pygame.init()



FALL = os.environ.get('FALL', '0') != '0'

if FALL:
	from inference_sdk import InferenceHTTPClient

	CLIENT = InferenceHTTPClient(
		#api_url="http://localhost:9001",
		api_url="https://detect.roboflow.com",
		api_key=os.environ['INFERENCE_API_KEY']
	)


def create_window():

	# create an empty window
	#pygame.display.set_mode((1800, 1000))
	pygame.display.set_mode((1000, 700))
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
	
		#print('list dirs and files...')
		for dir in rootdirs:
			#print(dir)
			for root, dirs, files in os.walk(dir):
				#print('root, dirs, files: ' + str(root) + ' ' + str(dirs) + ' ' + str(files))
				for file in files:
					#print('lll file: ' + str(file))
					f = Path(os.path.join(root, file))
					if f.is_file():
						if str(f) not in allfiles:
							#print('found new file: ' + str(f))
							allfiles[str(f)] = f.stat().st_ctime
		
		#print('sort by ctime...')
		#allfiles.sort(key=lambda python_sucks: python_sucks[0])
		allfiles = dict(sorted(allfiles.items(), key=lambda item: item[1]))
		#print('len(allfiles):', len(allfiles))
		
		#print('play..')
		
		for f in list(allfiles.keys())[-1:]:
			if f not in seen:
				seen.append(f)
				#print(f)
				#print()
				#print()
			# 	
			# 	print(f'File: {f}')				
		
				#print(f'play file: {f}')				
				#cmd = f'MPLAYER_VERBOSE=-1 mplayer -msglevel all=0 -noautosub -wid {w} "{f}"'
				cmd = f'mpv --really-quiet --wid={w} "{f}"'
				#print(cmd)

				os.system(cmd)

				found = False

				if FALL:
					# fall-detection-real/2
					# human-fall/2
					
					inference = None
					try:
						inference = CLIENT.infer(f, model_id="fall_detection-vjdfb/2")
					except requests.exceptions.ConnectionError:
						subprocess.check_call(['espeak', 'connection error!'])
					except Exception as e:
						subprocess.check_call(['espeak', e])
					
					if inference:
							
						#print(json.dumps(inference, indent=2))
						for pr in inference.get('predictions', []):
							x = f'class {pr["class"]} {round(pr["confidence"]*100)}'
							print(x)
							subprocess.check_call(['espeak', x])				
							found = True
						
				if not found:
					subprocess.check_call(['espeak', 'motion!'])

		time.sleep(0.1)
		#print('---')
	

if __name__ == '__main__':
	print_hi('PyCharm')

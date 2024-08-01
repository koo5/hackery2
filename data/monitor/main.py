#!/usr/bin/env python3

import sys,os,time
import subprocess
import re
import time, json, subprocess
from pathlib import Path
import pygame
import requests
import fire


def main(path, lookback=50, speak=True):


	
	FALL = os.environ.get('FALL', '0') != '0'
	CHATGPT = os.environ.get('CHATGPT', '0') != '0'
	
	
	if FALL:
		from inference_sdk import InferenceHTTPClient
	
		CLIENT = InferenceHTTPClient(
			#api_url="http://localhost:9001",
			api_url="https://detect.roboflow.com",
			api_key=os.environ['INFERENCE_API_KEY']
		)
	
	elif CHATGPT:
		from oai import oai
	
	def create_window():
	
		title = f'KOOMVCR{time.time()}'
	
		# create an empty window, sized to the screen resolution - 200 but not fullscreen
		pygame.display.set_mode((pygame.display.Info().current_w - 200, pygame.display.Info().current_h - 200))
		#pygame.display.set_mode((1000, 700))
		pygame.display.set_caption(title)
		pygame.display.flip()
		
	
		# get the window id
		time.sleep(1)
		window_id = subprocess.check_output(['xwininfo', '-name', title]).decode()
		window_id = re.search('Window id: (0x[0-9a-f]+)', window_id).group(1)
	
		print(f'Window id: {window_id}')
	
		return window_id
	
	seen = []


	pygame.init()
	w = create_window()

	
	rootdirs = [path]
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
		hh = sorted(allfiles.items(), key=lambda item: item[1])
		
		# sort files by name within directories
		#hh = sorted(hh, key=lambda item: Path(item[0]).name)

		allfiles = dict(hh)
		#print('len(allfiles):', len(allfiles))
		
		#print('play..')
		
		latest = list(allfiles.keys())[-lookback:]
		
		for f in latest:
			if f not in seen:
				seen.append(f)
				#print(f)
				#print()
				#print()
			# 	
				#if not FALL:
				print(f'File: {f}')
				
				subprocess.check_call(['notify-send --expire-time=3000 -i /usr/share/icons/gnome/48x48/status/dialog-information.png "Playing" "' + f + '"'], shell=True)  				
		
				#print(f'play file: {f}')				
				#cmd = f'MPLAYER_VERBOSE=-1 mplayer -msglevel all=0 -noautosub -wid {w} "{f}"'
				cmd = f'mpv --really-quiet --wid={w} "{f}"'
				#print(cmd)
				
				subprocess.Popen(cmd, shell=True)

				found = False

				if f is latest[-1]:
	
					if FALL:
						
						inference = None
						try:
							# tried:
							# fall-detection-real/2
							# human-fall/2
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
	
					elif CHATGPT:
						reply = {}
						try:
							reply = oai([f])
							emergency = reply.get('emergency')
						except Exception as e:
							subprocess.check_call(['espeak', f'Error: {e}'])
						else:
							if emergency != "none":
								subprocess.check_call(['espeak', f'Emergency: {emergency}. Description: {reply.get("image_contents")}, Explanation: {reply.get("explanation")}'])
								found = True
					
							
				if not found and speak:
					subprocess.check_call(['espeak', 'motion!'])
					
		time.sleep(0.1)
		print('---')
	

if __name__ == '__main__':
	fire.Fire(main)

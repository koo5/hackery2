#!/usr/bin/env python3

import sys, os, time
import subprocess
import re
import time, json, subprocess
from pathlib import Path
import pygame
import requests
import fire

_camera_id = 0


def main(path, lookback=50, speak=True, prompt='', CHATGPT=False, ROBOFLOW=False, camera_id=0, localization=False):
	global _camera_id
	_camera_id = camera_id

	if ROBOFLOW:
		from inference_sdk import InferenceHTTPClient

		CLIENT = InferenceHTTPClient(
			# api_url="http://localhost:9001",
			api_url="https://detect.roboflow.com",
			api_key=os.environ['INFERENCE_API_KEY']
		)

	elif CHATGPT:
		from oai import oai

	def create_window():

		title = f'KOOMVCR{time.time()}'

		# create an empty window, sized to the screen resolution - 200 but not fullscreen
		pygame.display.set_mode((pygame.display.Info().current_w - 400, pygame.display.Info().current_h - 200))
		# pygame.display.set_mode((1000, 700))
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

		# print('list dirs and files...')
		for dir in rootdirs:
			# print(dir)
			for root, dirs, files in os.walk(dir):
				# print('root, dirs, files: ' + str(root) + ' ' + str(dirs) + ' ' + str(files))
				for file in files:
					# print('lll file: ' + str(file))
					f = Path(os.path.join(root, file))
					if f.is_file():
						if str(f) not in allfiles:
							# print('found new file: ' + str(f))
							allfiles[str(f)] = f.stat().st_ctime

		# print('sort by ctime...')
		# allfiles.sort(key=lambda python_sucks: python_sucks[0])
		hh = sorted(allfiles.items(), key=lambda item: item[1])

		# sort files by name within directories
		# hh = sorted(hh, key=lambda item: Path(item[0]).name)

		allfiles = dict(hh)
		# print('len(allfiles):', len(allfiles))

		# print('play..')

		all = list(allfiles.keys())
		tail = all[-1000:]
		latest = all[-lookback:]
		latest_imgs = [f for f in tail if any([f.endswith(ext) for ext in 'jpg;webp;avif;jpeg;png'.split(';')])]

		mqtt_pub('loop', 1)

		latests = [f for f in latest if f not in seen]

		if len(latests):
			print('sleep to accumulate more images ..')
			time.sleep(5)

		for f in latests:

			seen.append(f)

			print(f'File: {f}')

			subprocess.check_call([
				'notify-send --expire-time=3000 -i /usr/share/icons/gnome/48x48/status/dialog-information.png "Playing" "' + f + '"'],
				shell=True)
			# print(f'play file: {f}')
			# cmd = f'MPLAYER_VERBOSE=-1 mplayer -msglevel all=0 -noautosub -wid {w} "{f}"'
			# cmd = f'mpv --really-quiet --wid={w} "{f}"'
			cmd = f'mpv --vo=x11 --wid={w} "{f}"'
			# print(cmd)

			# subprocess.Popen(cmd, shell=True)
			subprocess.call(cmd, shell=True)

			# did we indicate (through espeak) that we found/processed the image
			indicated = False
			inference_service_used = False

			mqtt_pub('motion', 1)

			if len(latest_imgs) and (f is latest_imgs[-1]):

				if ROBOFLOW or CHATGPT:
					inference_service_used = True

				if ROBOFLOW:

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

						# print(json.dumps(inference, indent=2))
						for pr in inference.get('predictions', []):
							x = f'class {pr["class"]} {round(pr["confidence"] * 100)}'
							print(x)
							subprocess.check_call(['espeak', x])
							indicated = True

				if CHATGPT:
					print('chatgpt')

					try:
						reel = []
						if len(latest_imgs) > 9:
							reel.append(latest_imgs[-9])
						if len(latest_imgs) > 5:
							reel.append(latest_imgs[-5])
						elif len(latest_imgs) > 2:
							reel.append(latest_imgs[-2])
						reel.append(f)

						print('reel:', reel)

						reply = oai(reel, prompt)
						emergency = reply.get('emergency')
					except Exception as e:
						print(e)
						subprocess.check_call(['espeak', f'Error: {e}'])
					else:
						print('emergency:', emergency.__repr__())
						mqtt_pub('chatgpt/emergency', 0 if emergency == 'none' else 1)
						description = reply.get("image_contents")
						description_localized = reply.get("image_contents_localized")
						if emergency != "none":
							mqtt_pub('chatgpt/description', description)
							indicated = True

						if speak:
							subprocess.check_call(['espeak', f'Emergency: {emergency}'])
							if localization:
								subprocess.check_call(['espeak', '-v', 'czech', f'Popis: {description_localized}'])
							else:
								subprocess.check_call(['espeak', f'Description: {description}'])
						subprocess.check_call(['espeak', f'Explanation: {reply.get("explanation")}'])

			if not indicated and speak:
				subprocess.check_call(['espeak', 'motion!'])

			if inference_service_used:
				sleep_remaining_secs = 60
				while sleep_remaining_secs > 0:
					print(f'sleeping... {sleep_remaining_secs}')
					time.sleep(1)
					sleep_remaining_secs -= 1

		time.sleep(0.1)
		print('---')


hostname = subprocess.check_output(['hostname']).decode().strip()


def mqtt_pub(topic, value):
	topic = hostname + str(_camera_id) + '/' + topic + '/state'
	h = os.environ.get('MQTT_HOST', None)
	if h is None:
		print('MQTT_HOST not set')
		return
	p = int(os.environ.get('MQTT_PORT', 1883))
	import paho.mqtt.publish as publish
	auth = {}
	if os.environ.get('MQTT_USER', None):
		auth['username'] = os.environ.get('MQTT_USER')
	if os.environ.get('MQTT_PASS', None):
		auth['password'] = os.environ.get('MQTT_PASS')
	publish.single(topic, str(value), hostname=h, port=p, auth=auth, qos=1, retain=True)
	print(f'Published {value} to {topic} on {h}:{p}')


if __name__ == '__main__':
	fire.Fire(main)

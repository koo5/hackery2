#!/usr/bin/env python3

import os, time, sys, shutil, errno, subprocess, shlex
from datetime import datetime
import cv2
from PIL import Image
import numpy as np
import sys
import glob
import os
from subprocess import call
from urllib.request import urlopen
from collections import Counter
import json
from pathlib import Path
import re
import pathlib
import pygame
import numpy as np
from mss import mss
from PIL import Image
import pytesseract



dest_dir = os.path.abspath(sys.argv[1])
pathlib.Path('data').mkdir(exist_ok=True)



def get_opencv_img_res(opencv_image):
	height, width = opencv_image.shape[:2]
	return width, height



def convert_opencv_img_to_pygame(opencv_image):
	"""
	Convert OpenCV images for Pygame.
	see https://gist.github.com/radames/1e7c794842755683162b
	"""
	rgb_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
	#Generate a Surface for drawing images with Pygame based on OpenCV images
	pygame_image = pygame.surfarray.make_surface(rgb_image)

	return pygame_image



def safe_move(src, dst):
	"""Rename a file from ``src`` to ``dst``.

	*   Moves must be atomic.  ``shutil.move()`` is not atomic.
		Note that multiple threads may try to write to the cache at once,
		so atomicity is required to ensure the serving on one thread doesn't
		pick up a partially saved image from another thread.

	*   Moves must work across filesystems.  Often temp directories and the
		cache directories live on different filesystems.  ``os.rename()`` can
		throw errors if run across filesystems.

	So we try ``os.rename()``, but if we detect a cross-filesystem copy, we
	switch to ``shutil.move()`` with some wrappers to make it atomic.

	https://alexwlchan.net/2019/03/atomic-cross-filesystem-moves-in-python/

	"""
	try:
		os.rename(src, dst)
	except OSError as err:

		if err.errno == errno.EXDEV:
			# Generate a unique ID, and copy `<src>` to the target directory
			# with a temporary name `<dst>.<ID>.tmp`.  Because we're copying
			# across a filesystem boundary, this initial copy may not be
			# atomic.  We intersperse a random UUID so if different processes
			# are copying into `<dst>`, they don't overlap in their tmp copies.
			copy_id = uuid.uuid4()
			tmp_dst = "%s.%s.tmp" % (dst, copy_id)
			shutil.copyfile(src, tmp_dst)

			# Then do an atomic rename onto the new name, and clean up the
			# source image.
			os.rename(tmp_dst, dst)
			os.unlink(src)
		else:
			raise




tmp_fn = '/tmp/screenshot-whole-loop.png'
try:
	os.makedirs(dest_dir)
except FileExistsError:
	pass


i = 0
def print_free_space_very_smartly():
	global i
	if i == 0:
		os.system("df -h " + dest_dir)
	i += 1
	if i == 100:
		i = 0


def init_cam():
	print("Accessing device's camera...")
	cap = cv2.VideoCapture(2)
	cap.set(3, 1920)
	cap.set(4, 1080)
	print("Camera ready!")
	return cap



def camloop():
	try:
		while (True):
			cap = init_cam()
			_, frame = cap.read()

			# this would make the detection fail if text and background didn't have different luminosity i guess
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

			#blur = cv2.GaussianBlur(gray,(10,10),0)
			#_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

			cv2.imshow('Frame', gray)
			cv2.imwrite('file.png', gray)

			tessfunc()
	except:
		pass
	finally:
		cap.release()
	exit()


def scrotloop_with_standalone_tesseract():
	while True:
		print_free_space_very_smartly()
		dest_fn = dest_dir + "/" + datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S.%f") + ".png"
		tmp_fn = dest_dir + '/tmp'
		cmd = ["scrot", "-o", '-q', '0', '-u'] + [tmp_fn]
		print(cmd)
		subprocess.check_call(cmd)
		safe_move(tmp_fn, dest_fn)
		link = dest_dir + '/' + 'last.png'
		os.unlink(link)
		os.symlink(dest_fn, link)
		print(dest_fn)

		img = cv2.cvtColor(cv2.imread(dest_fn), cv2.COLOR_BGR2GRAY)
		_, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
		cv2.imwrite('data/file.png', thresh)

		#os.system('geeqie -r --first')
		#os.system("tesseract --psm 11 --dpi 300 " + link + ' data')
		os.system("tesseract --psm 11 --dpi 300 " + 'data/file.png' + ' data/data')
		
		with open('data/output.txt', 'w') as output_file:
			with open('data/data.txt', 'r') as mf:
				out = "\n********************************************"
				for line in mf.readlines():
					l = line.strip().strip('\n')
					if len(l) > 4 and not l.isspace():
						out += l + '\n'
				out += "********************************************"
				print(out, file=output_file)
				print(file=output_file)
		time.sleep(int(sys.argv[2]))



def screenshot():
	print_free_space_very_smartly()
	dest_fn = dest_dir + "/" + datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S.%f") + ".png"
	tmp_fn = dest_dir + '/tmp'
	cmd = ["scrot", "-o", '-q', '100', '-u'] + [tmp_fn]
	sys.stdout.write(shlex.join(cmd))
	subprocess.check_call(cmd)
	safe_move(tmp_fn, dest_fn)
	link = dest_dir + '/' + 'last.png'
	os.unlink(link)
	os.symlink(dest_fn, link)
	#print(dest_fn)
	return dest_fn





_t = None
def t():
	global _t
	t2 = time.perf_counter()
	if _t is not None:
		print(' ' + str(round(t2 - _t, 3)))
	_t = t2


#res = (3840,2160)
res = (1920,1000)

def scrotloop_with_tesseract_api(sct):
	try:

		pygame.init()
		screen = pygame.display.set_mode(res)



		# print(f'Conversion time: {time_end - time_start}Seconds/ {1/(time_end - time_start)}fps')

		while True:
			t()
			mon = {'left': 0, 'top': 0, 'width': res[0], 'height': res[1]}

			sys.stdout.write(' | grab..')
			screenShot = sct.grab(mon)
			img = np.array(screenShot)
			#img = np.array(Image.frombytes('RGB', (screenShot.width, screenShot.height), screenShot.rgb,))
			t()

			sys.stdout.write(' | image_to_data..')
			results = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
			t()

			sys.stdout.write(' | rectangle..')
			for i in range(0, len(results["text"])):
				x = results["left"][i]
				y = results["top"][i]
				w = results["width"][i]
				h = results["height"][i]
				text = results["text"][i]
				conf = int(results["conf"][i])
				text = text.strip()
				#if len(text) > 4:
				#	print((x,y,w,h,text,conf))
				if len(text) > 3:
					cv2.rectangle(img, (x,y), (x+w,y+h),  (255, 255, 0), 2)
			t()
			#cv2.imwrite('data/'+datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S.%f") + ".png", img)
			#gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
			#cv2.imshow('boxes', img)
			#cv2.waitKey(0)

			sys.stdout.write(' | img_to_pygame..')
			pygame_image = convert_opencv_img_to_pygame(img)
			sys.stdout.write(' | blit...')
			screen.blit(pygame_image, (0, 0))
			sys.stdout.write(' | display.update..')
			pygame.display.update()
			t()

			print(' :) ')

	finally:
		pygame.quit()


if __name__ == '__main__':
	with mss() as sct:
		scrotloop_with_tesseract_api(sct)


# levenshtein

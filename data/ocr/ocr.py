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





dest_dir = os.path.abspath(sys.argv[1])
pathlib.Path('data').mkdir(exist_ok=True)



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




def scrotloop():
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


scrotloop()



# levenshtein

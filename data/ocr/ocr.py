#!/usr/bin/env python3

from av.video.frame import VideoFrame
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



_t = None
def t(upcoming_op):
	global _t
	t2 = time.perf_counter()
	if _t is not None:
		sys.stdout.write(' ' + str(round(t2 - _t, 3)) + 's')
		sys.stdout.write('\n')
	if upcoming_op is not None:
		sys.stdout.write(' | ' + upcoming_op + '..')
		_t = t2
	else:
		_t = None



def rects_list(results):
	rects0 = []
	for i in range(0, len(results["text"])):
		x = results["left"][i]
		y = results["top"][i]
		w = results["width"][i]
		h = results["height"][i]
		text = results["text"][i]
		conf = int(results["conf"][i])
		text = text.strip()
		rects0.append({'x':x,'y':y,'w':w,'h':h,'text':text,'conf':conf})
	return rects0




grab_res = (3840,2160)
output_window_res = (3840,2160)

def mss_loop_with_tesseract_api(sct):
	try:

		#os.environ['SDL_VIDEO_WINDOW_POS'] = f"{res[0]},{res[1]}"

		pygame.init()
		screen = pygame.display.set_mode(output_window_res)#, flags=pygame.NOFRAME)
		while True:
			t('grab')
			mon = {'left': 0, 'top': 0, 'width': grab_res[0], 'height': grab_res[1]}

			screenShot = sct.grab(mon)
			img0 = np.array(screenShot)
			#img = np.array(Image.frombytes('RGB', (screenShot.width, screenShot.height), screenShot.rgb,))




			# text *detection* might go here.
			# https://github.com/LaggyHammer/real-time-OCR/blob/master/real_time_ocr_multiprocessing.py
			# https://pyimagesearch.com/2018/08/20/opencv-text-detection-east-text-detector/
			# whats this? https://github.com/opencv/opencv/blob/master/samples/dnn/text_detection.cpp
			# Note that we don't need to rely on EAST only, we can also do something like the table cell detection linked here https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html

			# roi_list = east_stuff(...




			# seems that different versions of tesseract support or dont support non-grayscale images, 
			# and different preprocessing steps help or hinder different testcases. So, it seems that we should do a couple permutations,
			# at least color/grayscale / blurred/nonblurred / thresholded/nonthresholded
			# and just scan for PII in all of them
			# | While tesseract version 3.05 (and older) handle inverted image (dark background and light text) without problem, for 4.x version use dark text on light background.
			# https://towardsdatascience.com/getting-started-with-tesseract-part-ii-f7f9a0899b3f
			# https://tesseract-ocr.github.io/tessdoc/ImproveQuality.html
			# https://vovaprivalov.medium.com/tesseract-ocr-tips-custom-dictionary-to-improve-ocr-d2b9cd17850b


			# the optional preprocessing steps
			img = img0#cv2.cvtColor(img0, cv2.COLOR_BGR2GRAY)
			img = cv2.GaussianBlur(img,(5,5),0)
			#_, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
			#img = 255-img



			t('image_to_data')

			# the recognition itself. psm is important. also --oem
			# also: You can extend the standard dictionary for a language model with your own words or retrain the model replacing completely the standard dictionary words with your own words.
			# also, there are 5 versions of tesseract
			results = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config='--psm 11 --oem 3')


			# take what we fed into tesseract and prepare it for drawing over it and displaying it on screen
			img0 = img#cv2.cvtColor(img, cv2.COLOR_GRAY2RGBA)

			t('rectangle')
			rects0 = rects_list(results)
			# sort rects by area...helps (somewhat) with big rects drawing over small rects
			rects = sorted(rects0, key=lambda r:r['w']*r['h'], reverse=True)


			shapes = np.zeros_like(img0, np.uint8)
			#shapes = np.zeros((grab_res[1],grab_res[0],3), np.uint8)


			for rect in rects:
				x,y,w,h,text,conf = rect['x'],rect['y'],rect['w'],rect['h'],rect['text'],rect['conf']				

				#if len(text) > 4:
				#	print((x,y,w,h,text,conf))
				if len(text) > 0:
					# draw orange rectangle over detected text
					cv2.rectangle(img0, (x,y), (x+w,y+h),  (0, 0, 0), cv2.FILLED)
					# draw a rectangle around detected text
					#cv2.line(img0, (x,y-2), (x+w,y-2),  (0, 200, 200), 1)
					#cv2.line(img0, (x-2,y), (x-2,y+h),  (200, 200, 0), 1)


			mask = shapes.astype(bool)
			cv2.addWeighted(shapes, 0.3, img0, 0.5, 0, img0)
			#img0[mask] = cv2.addWeighted(img0, 0.8, shapes, 0.2, 0)[mask]
			#cv2.bitwise_and(img0, 0, shapes, 1)


			for rect in rects:
				x,y,w,h,text,conf = rect['x'],rect['y'],rect['w'],rect['h'],rect['text'],rect['conf']
				if len(text) > 0:
					# draw line above detected text
					#cv2.rectangle(img0, (x-1,y-1), (x+w+2,y+h+2),  (0, 255, 255), 1)
					#cv2.rectangle(img0, (x-2,y-2), (x+w+4,y+h+4),  (255, 0, 0), 1)
					# underline detected text(?)
					cv2.line(img0, (x,y),(x+w,y),  (0, 200, 200), 1)
					# draw the detected text
					text_size = 0.8
					cv2.putText(img0, text, (x,y+int(0.9*h)), cv2.FONT_HERSHEY_SIMPLEX, text_size, (0,155,0), 2, cv2.LINE_AA, False)





			t('img_to_pygame')
			pygame_image = convert_opencv_img_to_pygame(img0)
			pygame_image = pygame.transform.scale(pygame_image, output_window_res)
			t('blit')
			screen.blit(pygame_image, (0, 0))
			t('display.update')
			pygame.display.update()
			
			t(None)
			print('and loop.')

	finally:
		pygame.quit()


if __name__ == '__main__':
	with mss() as sct:
		mss_loop_with_tesseract_api(sct)


#
# levenshtein





# for video input/output:
# https://github.com/Abhishek325/OCR-live-stream

# for v4l loopback:
# https://github.com/Abhishek325/OCR-live-stream



# https://github.com/mftnakrsu/Comparison-of-OCR/blob/main/ocr.py
# ^ we should start here
# - https://towardsdatascience.com/remove-text-from-images-using-cv2-and-keras-ocr-24e7612ae4f4


# not sure if/where this fits: https://news.ycombinator.com/item?id=29554433
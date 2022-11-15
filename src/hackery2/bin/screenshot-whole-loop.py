#!/usr/bin/env python3
import os, time, sys, shutil
from datetime import datetime


i = 0

def print_free_space_very_smartly():
	global i
	if i == 0:
		os.system("df -h " + sys.argv[1])
	#else:
	#	os.system("df -h " + sys.argv[1] + " | tail -n 1")
	i += 1
	if i > 10:
		i = 0


# the arguments to the script are: folder, delay, scrot args

tmp_fn = '/tmp/screenshot-whole-loop.png'
dest_dir = os.path.abspath(sys.argv[1])
try:
	os.makedirs(dest_dir)
except FileExistsError:
	pass

while True:
	dest_fn = dest_dir + "/" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S.%f") + ".png"
	print(dest_fn)
	cmd = "scrot  -q 0  " +sys.argv[3]+ " " + tmp_fn
	print(cmd)
	os.system(cmd)
	shutil.move(tmp_fn, dest_fn)	
	#os.system('geeqie -r --first')
	print_free_space_very_smartly()
	time.sleep(int(sys.argv[2]))



# generate video with crop:
# ffmpeg -framerate 1 -pattern_type glob -i '*.png'   -c:v libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -vf "crop=1920:1080:0:0"   (date --utc "+%Y-%m-%d_%H-%M-%S.%N").mp4


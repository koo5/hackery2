#!/usr/bin/env python3
import os, time, sys, shutil, errno, subprocess, shlex, uuid
from datetime import datetime


# the arguments to the script are: folder, delay, scrot args
# example invocation: screenshot-whole-loop.py ~/screenshots 0 -q 75 -p


dest_dir = os.path.abspath(sys.argv[1])




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



tmp_dir = dest_dir + '/tmp'
tmp_fn = tmp_dir + '/screenshot-whole-loop.png'
try:
	os.makedirs(dest_dir)
except FileExistsError:
	pass
try:
	os.makedirs(tmp_dir)
except FileExistsError:
	pass


i = 0
def print_free_space_very_smartly():
	global i
	if i == 0:
		os.system("df -h " + dest_dir)
	i += 1
	if i == 10:
		i = 0


while True:
	print_free_space_very_smartly()
	dest_fn = dest_dir + "/utc" + datetime.utcnow().strftime("%Y_%m_%d_%H_%M_%S.%f") + ".png"
	cmd = ["scrot", "-o"] + sys.argv[3:] + [tmp_fn]
	#print(cmd)
	subprocess.check_call(cmd)
	safe_move(tmp_fn, dest_fn)
	symlink = dest_dir + '/' + 'last.png'
	try:
		os.remove(symlink)
	except OSError:
		pass
	os.symlink(dest_fn, symlink)
	print(dest_fn)
	#os.system('geeqie -r --first')
	time.sleep(int(sys.argv[2]))



# notes:
# generate video with crop:
# ffmpeg -framerate 1 -pattern_type glob -i '*.png'   -c:v libx264 -pix_fmt yuv420p -vf "pad=ceil(iw/2)*2:ceil(ih/2)*2" -vf "crop=1920:1080:0:0"   (date --utc "+%Y-%m-%d_%H-%M-%S.%N").mp4


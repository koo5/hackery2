#!/usr/bin/env python3
import subprocess, shlex, os, logging


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


while True:
	try:
		process = subprocess.Popen(shlex.split('journalctl -f /usr/lib/systemd/systemd-logind -n 0'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
		for line in process.stdout:
			print(line.__repr__())
			log.info(line)
			line = line.strip()
			if 'Power key pressed' in line:
				log.info('sleep..')
				print('sleep..')
				os.system('/home/koom/hackery2/src/hackery2/bin/sleep.sh&')
	except Exception as e:
		print(e)
		log.error(e)


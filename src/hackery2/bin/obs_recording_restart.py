#!/usr/bin/env python3


import subprocess,shlex,time,datetime,sys

def co(x):
	print('cmd:'+x)
	try:
		r = subprocess.check_output(shlex.split(x), text=True)
	except Exception as e:
		print(e.output)
		raise

	print('result:'+r)
	if r != '':
		r = r.splitlines()[0]
	time.sleep(0.25)
	return r

co('sudo -u koom obs-cli --password ccfa0506 label text zzz "' + datetime.datetime.now().isoformat() + '"')
co('sudo -u koom obs-cli --password ccfa0506 sceneitem hide ding ding_ogg')
co('sudo -u koom obs-cli --password ccfa0506 sceneitem show ding zzz')

if len(sys.argv) > 1 and sys.argv[1] == 'start':
	pass
else:
	if co('sudo -u koom obs-cli --password ccfa0506 recording status') != 'Recording: true':
		exit()
	co('sudo -u koom obs-cli --password ccfa0506 recording stop')

	#co('xcalib -a -i')
	#co('/home/koom/xrandr-invert-colors/xrandr-invert-colors -s 0')

	while True:
		try:
			if co('obs-cli --password ccfa0506 recording status') == 'Recording: false':
				break
		time.sleep(0.5)
		except:
			pass

	#co('xcalib -a -i')
	#co('/home/koom/xrandr-invert-colors/xrandr-invert-colors -s 0')

co('obs-cli --password ccfa0506 recording start')
co('sudo -u koom obs-cli --password ccfa0506 sceneitem show ding ding_ogg')
co('sudo -u koom obs-cli --password ccfa0506 label text zzz " "')
co('sudo -u koom obs-cli --password ccfa0506 sceneitem hide ding zzz')

#while True:
#	if co('obs-cli --password ccfa0506 recording status') == 'Recording: true':
#		break



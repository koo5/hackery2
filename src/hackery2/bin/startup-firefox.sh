#!/usr/bin/env python3

import subprocess, shlex, os

f = subprocess.check_output(['/usr/bin/which', 'firefox'], text=True)
if f.startswith('/usr/bin/'):
	print('firefox is from apt')
	subprocess.check_call(['security_updates.sh'])
else:
	print('firefox is from snap, i think')
	subprocess.check_call(shlex.split('sudo snap refresh firefox'))
os.system('firefox')


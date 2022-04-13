#!/usr/bin/env python3


import os,sys,subprocess,time,shlex,logging, pathlib


def get_username(url):
	try:
		return url.rstrip('/').split('/')[-2].split(':')[-1]
	except:
		return None

url = sys.argv[1]
username = get_username(url)
if username != None:
	pathlib.Path(username).mkdir(exist_ok=True)
	os.chdir(username)
subprocess.check_call(['git', 'clone', '--recurse-submodules'] + sys.argv[1:-1] + [url])

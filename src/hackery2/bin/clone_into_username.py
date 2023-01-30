#!/usr/bin/env python3


import logging,os,sys,subprocess,time,shlex,logging, pathlib, urllib, json

urlstr = sys.argv[1]
optional_clone_parameters = sys.argv[1:-1]

url = urllib.parse.urlparse(urlstr)
logging.warning(str(url))
path = url.path.strip('/').split(':')[-1].split('/')
user = path[0]
proj = path[1].removesuffix('.git')
d = os.path.expanduser('~/repos/'+user+'/'+proj+'/0/')

pathlib.Path(d).mkdir(exist_ok=True,parents=True)
os.chdir(d)
print(json.dumps({'filesystem_path': d + proj}))

cmd = ['git', 'clone', '--recurse-submodules'] + optional_clone_parameters + [urlstr]
sys.exit(subprocess.call(cmd))

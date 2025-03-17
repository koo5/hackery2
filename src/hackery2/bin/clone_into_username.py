#!/usr/bin/env python3

#this file is cc by-sa 3.0 with attribution required, because it is mostly just bits from SO pasted together

import json
#import urllib2, urllib
#import urllib
import urllib.request, urllib.parse
import sys, os

try:
	import xdg.BaseDirectory
	cachedir = xdg.BaseDirectory.xdg_cache_home + '/getgit'
except:
	from os.path import expanduser
	cachedir = expanduser("~"+'/.getgit')



#http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
import os, errno
def mkdir_p(path):
	try:
		os.makedirs(path)
	except OSError as exc: # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise
#Update #For Python ≥ 3.2, os.makedirs has an optional third argument exist_ok that, when true, enables the mkdir -p functionality —unless mode is provided and the existing directory has different permissions than the intended ones; in that case, OSError is raised as previously.

mkdir_p(cachedir)

last_search = cachedir +'/'+"last_search"





import logging,os,sys,subprocess,time,shlex,logging, pathlib, urllib, json, click
logger = logging.getLogger('ciu')


def removesuffix(self: str, suffix: str, /) -> str:
    if self.endswith(suffix):
        return self[:-len(suffix)]
    else:
        return self[:]




def name_search(s):
	##TODO
	f = urllib.request.urlopen("https://api.github.com/search/repositories?q=" + urllib.parse.quote_plus(s)).read()
	#open("debug_result", "w").write(f)
	x = json.loads(f) #at least you didnt see my fuck ups except for that one
	r = []
	for i,j in enumerate(x['items']):
		 r.append((i, j['full_name'])) #todo: save the clone command here, along with the name
	return r

#all that needs to happen is for the top result to be selected automagically

def num_search(num):
	f = open(last_search, "r")
	g = json.load(f)
	for i in g:
		num = str(i[0])
		name = i[1]
		#print num, lookie, len(num), len(lookie), 
		if lookie == num:
			return name

"""two phase search, first enter text, get a list of numbered results, they are saved in last_results, then call this 
again with a number"""



@click.command()
@click.argument('lookie', nargs=1)
@click.argument('optional_clone_args', nargs=-1)
def magic(lookie, **kwargs):
	for xx in ['git clone', '$ git clone', '$git clone']:
		if lookie.startswith(xx):
			lookie = lookie[len(xx):]
			break

	lookie.trim()

	try:
		url = urllib.parse.urlparse(lookie)
	except:
		url = None

	logger.info(url)

	if url and url.path and (url.path.startswith('git@') or url.scheme):
		clone(lookie, **kwargs)

	elif lookie.isdigit():
		name = num_search(lookie)
		if name == None:
			logger.info( "wat")
		else:
			clone("https://github.com/"+name+".git", **kwargs)
	
	else:
		res = name_search(lookie)
		if not res:
			logger.info ("I can pretty safely say that there were no results.")
		else:
			sans_first = res[1:]
			other = sans_first[:4]
			if len(other):
				logger.info ("other "+lookie+":")
				for i in other:
					logger.info (i[1])
				if len(other) < len(sans_first):
					logger.info ("...")
			try:
				logger.info ("Cloning " + res[0][1] + "...")
				clone("https://github.com/"+res[0][1]+".git", **kwargs)
			except Exception as e:
				logger.info ("An error occured:", e)

		#save it for later
		o = open(last_search, "w")
		json.dump(res, o, indent = 4)
		o.close()


def clone(url, optional_clone_args):

	url_parsed = urllib.parse.urlparse(url)
	logger.info(str(url_parsed))

	# taking the right side of a possible comma makes it handle both a https schema and a ssh schema
	path_cleaned = url_parsed.path.strip('/').split(':')[-1]
	path_cleaned = removesuffix(path_cleaned ,'.git')
	logger.info('path_cleaned: ' + path_cleaned.__repr__())
	#path_cleaned = pathlib.Path(path_cleaned).resolve(strict=False)
	#path_cleaned.normalize()
	path_cleaned = str(path_cleaned)
	path_split = path_cleaned.split('/')
	
	#path = path_cleaned.split('/')
	#logger.info('path: ' + path.__repr__())
	#user = path[0]
	#proj = path[1]
	#logger.info('user: ' + user.__repr__())
	#logger.info('proj: ' + proj.__repr__())


	parent_fs_path = os.path.expanduser('~/repos/'+path_cleaned+'/0/')
	logger.info('parent_dir: ' + parent_fs_path.__repr__())

	pathlib.Path(parent_fs_path).mkdir(exist_ok=True,parents=True)
	os.chdir(parent_fs_path)

	repo_fs_path = parent_fs_path + path_split[-1]
	
	# stdout print for gclur wrapper fish function
	print('\n' + json.dumps({'repo_fs_path': repo_fs_path}))

	git_cmd = ['git', 'clone', '--recurse-submodules'] + list(optional_clone_args) + [url]
	logger.info('git_cmd: ' + shlex.join(git_cmd))
	sys.exit(subprocess.call(git_cmd))



if __name__ == '__main__':
	logging.basicConfig(level="INFO")
	magic()

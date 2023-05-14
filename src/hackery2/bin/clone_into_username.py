#!/usr/bin/env python3.10


import logging,os,sys,subprocess,time,shlex,logging, pathlib, urllib, json, click
logger = logging.getLogger('ciu')


def removesuffix(self: str, suffix: str, /) -> str:
    if self.endswith(suffix):
        return self[:-len(suffix)]
    else:
        return self[:]


@click.command()
@click.argument('url', nargs=1)
@click.argument('optional_clone_args', nargs=-1)
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
	print('\n' + json.dumps({'repo_fs_path': repo_fs_path}))

	git_cmd = ['git', 'clone', '--recurse-submodules'] + list(optional_clone_args) + [url]
	logger.info('git_cmd: ' + shlex.join(git_cmd))
	sys.exit(subprocess.call(git_cmd))



if __name__ == '__main__':
	logging.basicConfig(level="INFO")
	clone()

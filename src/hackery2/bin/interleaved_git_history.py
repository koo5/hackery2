#!/usr/bin/env python3

""" print interleaved git history of current directory and subdirectories """
import os
import shlex
import subprocess
from datetime import datetime
from pathlib import Path


def git_log(directory):
	""" get git log of a directory """
	cmd = ['git', 'log', '--pretty=format:%H %ct']
	print(shlex.join(cmd))
	result = subprocess.run(cmd, stdout=subprocess.PIPE, cwd=directory)
	r = result.stdout.decode('utf-8').splitlines()
	print(r)
	return r


def get_all_commits():
	""" get all commits from current directory and subdirectories """
	commits = []
	directories = [Path('.')] + [d for d in Path('.').iterdir() if d.is_dir() and (d / '.git').exists()]
	print(directories)
	for directory in directories:
		print(directory)
		for line in git_log(directory):
			commit_hash, commit_time = line.split()
			commits.append((commit_hash, datetime.fromtimestamp(int(commit_time)), directory))
	return commits


def main():
	commits = get_all_commits()
	commits.sort(key=lambda x: x[1])  # sort by commit time
	for commit_hash, commit_time, directory in commits:
		print(f"{commit_time} {commit_hash} {directory}")


if __name__ == "__main__":
	main()

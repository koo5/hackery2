#!/usr/bin/env python3

""" print interleaved git history of current directory and subdirectories """
from datetime import datetime
from pathlib import Path
import git
import click
import logging
logger = logging.getLogger()


def git_log(directory):
	""" get git log of a directory """
	repo = git.Repo(directory)
	commits = []
	for commit in repo.iter_commits():
		commits.append({'hash': commit.hexsha, 'timestamp': datetime.fromtimestamp(commit.committed_date), 'committer': commit.committer.name, 'email': commit.committer.email, 'message': commit.message.split('\n')[0],  # Only take the first line of the commit message
			'directory': directory})
	return commits


def get_all_commits():
	""" get all commits from current directory and subdirectories """
	commits = []
	directories = [Path('.')] + [d for d in Path('.').iterdir() if d.is_dir() and (d / '.git').exists()]
	for directory in directories:
		commits.extend(git_log(directory))
	return commits


@click.command()
@click.option('--reverse', is_flag=True, help='Sort commits in reverse order')
def main(reverse):
	""" main function """
	commits = get_all_commits()
	commits.sort(key=lambda x: x['timestamp'])  # sort by commit time
	if reverse:
		commits.reverse()
	for commit in commits:
		email = commit['email']
		if True:#email in ['you@example.com', 'kolman.jindrich@gmail.com']:
			print(f"{commit['timestamp']} \t {commit['hash'][:6]} .. \t {commit['email']} \t {commit['directory']} \t {commit['message']}")
		else:
			print(f".............................................................{commit['email']} {commit['message']} {commit['directory']}")


# c: {commit['committer']}

if __name__ == "__main__":
	logging.basicConfig(level="INFO")
	main()

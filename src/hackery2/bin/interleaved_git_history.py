#!/usr/bin/env python3

""" print interleaved git history of current directory and subdirectories """
from datetime import datetime
from pathlib import Path
import git
import click
import logging
logger = logging.getLogger()


def git_log(repo):
	for branch in repo.branches:
		logger.info(f"Branch: {branch.name}")
		for commit in repo.iter_commits(branch):
			yield {'hash': commit.hexsha, 'timestamp': datetime.fromtimestamp(commit.committed_date), 'committer': commit.committer.name, 'email': commit.committer.email, 'message': commit.message.split('\n')[0],  # Only take the first line of the commit message
				'directory': repo.working_tree_dir, 'branch': branch.name}


def get_all_commits():
	""" get all commits from current directory and subdirectories """
	commits = []
	root = git.Repo('.')
	repos = [root] + [x.module() for x in root.iter_submodules()]
	for repo in repos:
		commits.extend(git_log(repo))
	# drop duplicates
	commits = list({commit['hash']: commit for commit in commits}.values())
	commits.sort(key=lambda x: x['timestamp'])  # sort by commit time
	return commits


@click.command()
@click.option('--reverse', is_flag=True, help='Sort commits in reverse order')
def main(reverse):
	""" main function """
	commits = get_all_commits()
	if reverse:
		commits.reverse()
	for commit in commits:
		email = commit['email']
		if True:#email in ['you@example.com', 'kolman.jindrich@gmail.com']:
			print(f"{commit['timestamp']} \t {commit['hash'][:8]} \t {commit['email']} \t{commit['branch']} \t {commit['directory']} \t {commit['message']}")
		else:
			print(f".............................................................{commit['email']} {commit['message']} {commit['directory']}")


# c: {commit['committer']}

if __name__ == "__main__":
	logging.basicConfig(level="INFO")
	main()

#!/usr/bin/env python3

""" print CSV of interleaved git history of current repo and submodules """
from datetime import datetime
from pathlib import Path
import git
import click
import logging
logger = logging.getLogger()


def git_log(commits, repo):
	logger.info(f"Repo: {repo.working_tree_dir}")

	logger.info("Branches:")
	for branch in repo.branches:
		logger.info(f"Branch: {branch.name}")
		get_commits(commits, repo, branch)

	logger.info("Remote branches:")
	for remote in repo.remotes:
		for branch in remote.refs:
			logger.info(f"Remote: {branch.name}")
			get_commits(commits, repo, branch)


def get_commits(commits, repo, branch):
	for commit in repo.iter_commits(branch):
		if commit.hexsha in commits:
			commits[commit.hexsha]['branches'].add(branch.name)
		else:
			commits[commit.hexsha] = {
				'branches': set([branch.name]),
				'hash': commit.hexsha,
				'timestamp': datetime.fromtimestamp(commit.committed_date),
				'committer': commit.committer.name,
				'author': commit.author.name,
				'email': commit.author.email,
				'message': commit.message.strip().replace('\n\n', ' | ').replace('\n\r', ' | ').replace('\r\n', ' | ').replace('\n', ' | ').replace('\r', ' | ').replace('\t', ' '),
				'directory': Path(repo.working_dir).relative_to(Path('.').absolute()),
				'branch': branch.name
			}


def get_all_commits():
	""" get all commits from current directory and subdirectories """
	commits = {}
	root = git.Repo('.')
	repos = [root] + [x.module() for x in root.iter_submodules()]
	for repo in repos:
		git_log(commits, repo)
	# drop duplicates
	commits = list(commits.values())
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
			print(f"{commit['hash'][:8]} ..\t{commit['timestamp']} \t {shorten(commit['email'])} \t{branches_presentation(commit['branches'])} \t {commit['directory']} \t {commit['message']}")
		else:
			print(f".............................................................{commit['email']} {commit['message']} {commit['directory']}")


# c: {commit['committer']}

def branches_presentation(branches):
	""" get branches presentation """

	branches2 = []
	for branch in list(branches):
		parts = branch.split('/')
		if len(parts) > 1:
			branches2.append(parts[1])
		else:
			branches2.append(branch)
	branches2 = list(set(branches2))

	if len(branches2) > 1:
		if 'HEAD' in branches2:
			branches2.remove('HEAD')

	branches2.sort(key=branch_sort_key)
	return shorten(', '.join(list(map(shorten, branches2))[:3]), 30)

def shorten(branch, l=20):
	if len(branch) > l:
		return branch[:l] + '..'
	return branch

def branch_sort_key(branch):
	if branch == 'HEAD':
		return (5, branch)
	if branch in ['master', 'main']:
		return (0, branch)
	return (1, branch)


if __name__ == "__main__":
	logging.basicConfig(level="INFO")
	main()

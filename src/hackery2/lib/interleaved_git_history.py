#!/usr/bin/env python3

""" print CSV of interleaved git history of current repo and submodules """
from datetime import datetime
from pathlib import Path
import git
import click
import logging
import os
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
				'directory': _get_relative_path(repo),
				'branch': branch.name
			}


def get_all_commits():
	commits = {}
	root = git.Repo('.')
	repos = []
	_collect_repos_recursively(root, repos)
	for repo in repos:
		git_log(commits, repo)
	# drop duplicates
	commits = list(commits.values())
	commits.sort(key=lambda x: x['timestamp'])  # sort by commit time
	return commits


def _get_relative_path(repo):
	"""Get the relative path of a repository from the root working directory."""
	try:
		root_path = Path('.').absolute()
		repo_path = Path(repo.working_tree_dir).absolute()
		return repo_path.relative_to(root_path)
	except ValueError:
		# If the repo is not under the current directory, return absolute path
		return repo_path


def _collect_repos_recursively(repo, repos_list):
	"""Recursively collect all repositories including nested submodules."""
	repos_list.append(repo)
	logger.info(f"Collecting commits from: {repo.working_tree_dir}")
	
	try:
		# Use iter_submodules with recurse=False to handle each level separately
		for submodule in repo.iter_submodules():
			if submodule.module_exists():
				try:
					# submodule.abspath is the absolute path to the submodule
					submodule_path = Path(submodule.abspath)
					logger.info(f"Checking submodule '{submodule.name}' at: {submodule_path}")
					
					if submodule_path.exists() and (submodule_path / '.git').exists():
						sub_repo = submodule.module()
						_collect_repos_recursively(sub_repo, repos_list)
					else:
						logger.warning(f"Submodule path does not exist or is not initialized: {submodule_path}")
				except Exception as e:
					logger.warning(f"Failed to access submodule {submodule.name}: {e}")
	except Exception as e:
		logger.warning(f"Failed to iterate submodules in {repo.working_tree_dir}: {e}")


@click.command()
@click.option('--reverse', is_flag=True, help='Sort commits in reverse order')
def main(reverse):
	commits = get_all_commits()
	if reverse:
		commits.reverse()
	for commit in commits:
		email = commit['email']
		print(f"{commit['hash'][:8]} ..\t{commit['timestamp']} \t {shorten(commit['email'])} \t{branches_presentation(commit['branches'])} \t {commit['directory']} \t {commit['message']}")


def branches_presentation(branches):
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
	log_level = os.environ.get('LOG_LEVEL', 'WARNING').upper()
	logging.basicConfig(level=log_level)
	main()

#!/usr/bin/env python3

""" print interleaved git history of current directory and subdirectories """
from datetime import datetime
from pathlib import Path
import git


def git_log(directory):
    """ get git log of a directory """
    repo = git.Repo(directory)
    commits = []
    for commit in repo.iter_commits():
        commits.append({
            'hash': commit.hexsha,
            'timestamp': datetime.fromtimestamp(commit.committed_date),
            'committer': commit.committer.name,
            'email': commit.committer.email,
            'message': commit.message.split('\n')[0],  # Only take the first line of the commit message
            'directory': directory
        })
    return commits


def get_all_commits():
    """ get all commits from current directory and subdirectories """
    commits = []
    directories = [Path('.')] + [d for d in Path('.').iterdir() if d.is_dir() and (d / '.git').exists()]
    for directory in directories:
        commits.extend(git_log(directory))
    return commits


def main():
    commits = get_all_commits()
    commits.sort(key=lambda x: x['timestamp'])  # sort by commit time
    for commit in commits:
        print(f"{commit['timestamp']} {commit['hash']} c: {commit['committer']} e: {commit['email']} m: {commit['message']} {commit['directory']}")


if __name__ == "__main__":
    main()
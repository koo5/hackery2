#!/bin/bash
# https://gist.githubusercontent.com/AbdElraoufSabri/7fac905f1ee08e9127a7d0ff4f08abb6/raw/71516e67e85378b9b8d26e548362150bfa4effcc/fix_github_https_repo.sh
#-- Script to automate https://help.github.com/articles/why-is-git-always-asking-for-my-password

REMOTE_NAME="$1"
REMOTE_NAME=${1-origin}
echo "fixing $REMOTE_NAME ..."

REPO_URL=`git remote -v | grep -m1 "^$REMOTE_NAME" | sed -Ene's#.*(https://[^[:space:]]*).*#\1#p'`
if [ -z "$REPO_URL" ]; then
  echo "-- ERROR:  Could not identify Repo url."
  echo "   It is possible this repo is already using SSH instead of HTTPS."
  exit
fi

USER=`echo $REPO_URL | sed -Ene's#https://github.com/([^/]*)/(.*)(\.git)?#\1#p'`
HOST=github.com
if [ -z "$USER" ]; then
  USER=`echo $REPO_URL | sed -Ene's#https://gitlab.com/([^/]*)/(.*)(\.git)?#\1#p'`
  HOST=gitlab.com
  if [ -z "$USER" ]; then
    echo "-- ERROR:  Could not identify User."
    exit
  fi
fi

REPO=`echo $REPO_URL | sed -Ene's#https://github.com/([^/]*)/(.*)#\2#p'`
if [ -z "$REPO" ]; then
  REPO=`echo $REPO_URL | sed -Ene's#https://gitlab.com/([^/]*)/(.*)#\2#p'`
  if [ -z "$REPO" ]; then
    echo "-- ERROR:  Could not identify Repo."
    exit
  fi
fi

NEW_URL="git@$HOST:$USER/$REPO"
echo "Changing repo url from "
echo "  '$REPO_URL'"
echo "      to "
echo "  '$NEW_URL'"
echo ""

CHANGE_CMD="git remote set-url $REMOTE_NAME $NEW_URL"
`$CHANGE_CMD`

echo "Success"

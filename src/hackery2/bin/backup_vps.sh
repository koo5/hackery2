#!/usr/bin/env fish

function e; or status --is-interactive; or exit 1; end

set MACHINE $argv[1]
set DSTDIR $argv[2]

mkdir -p $DSTDIR; e
sleep 5; e

rsync -av --progress -h -e hpnssh -r \
  --exclude 'dont_backup'  \
  --exclude 'venv' \
  --exclude '.cache'  \
  --exclude '__pycache__'  \
  --exclude '.npm'  \
  --exclude 'site-packages'  \
  --exclude 'node_modules'   \
  --exclude '/var/lib/docker/overlay2/'  \
  --exclude '/var/snap/docker/common/var-lib-docker/overlay2/'  \
  --exclude '/home/*/go/'  \
  --exclude '/home/*/.gradle/'  \
  --include '/var/***' \
  --include '/etc/***'  \
  --include '/root/***'  \
  --include '/home/***'   \
  --exclude '*'  \
  root@$MACHINE:// $DSTDIR/


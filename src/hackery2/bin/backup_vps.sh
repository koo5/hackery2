#!/usr/bin/env fish

function e; or status --is-interactive; or exit 1; end

set MACHINE $argv[1]
set DSTDIR $argv[2]

mkdir -p $DSTDIR; e
sleep 5; e

rsync -av --progress -h -e hpnssh -r $argv[3] \
  --exclude 'dont_backup'  \
  --exclude 'venv' \
  --exclude '.cache'  \
  --exclude '__pycache__'  \
  --exclude '.npm'  \
  --exclude 'site-packages'  \
  --exclude 'node_modules'   \
  --exclude '/var/cache/'  \
  --include '/var/lib/'   \
  --include '/var/lib/docker/'  \
  --include '/var/lib/docker/volumes/'  \
  --include '/var/lib/docker/volumes/***'  \
  --exclude '/var/log/***' \
  --exclude '/var/lib/***'  \
  --include '/var/snap/'  \
  --include '/var/snap/docker/'  \
  --include '/var/snap/docker/volumes/'  \
  --include '/var/snap/docker/volumes/***'  \
  --exclude '/var/snap/***'  \
  --include '/var/***' \
  --include '/etc/***'  \
  --include '/root/***'  \
  --exclude '/home/*/go/'  \
  --exclude '/home/*/.gradle/'  \
  --exclude '/home/*/.cargo/'  \
  --exclude '/home/*/.bun/'  \
  --include '/home/***'   \
  --exclude '*'  \
  root@$MACHINE:// $DSTDIR/


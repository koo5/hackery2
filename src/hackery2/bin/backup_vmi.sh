#!/usr/bin/env fish

set MACHINE $argv[1]
echo $MACHINE
set DATE (date '+%F-%H-%M-%S')
set DSTDIR "$MACHINE"_"$DATE"
echo $DSTDIR


rsync -av --progress -h   -e 'hpnssh -p 44' -r \
  --exclude 'dont_backup'  \
  --exclude 'venv' \
  --exclude '.cache'  \
  --exclude '__pycache__'  \
  --exclude '.npm'  \
  --exclude 'site-packages'  \
  --exclude 'node_modules'   \
  --exclude '/var/lib/docker/overlay2/'  \
  --exclude '/var/lib/docker/btrfs/subvolumes/'  \
  --exclude '/var/snap/docker/common/var-lib-docker/overlay2/'  \
  --exclude '/home/*/go/'  \
  --exclude '/home/*/.gradle/'  \
  --include '/var/***' \
  --include '/etc/***'  \
  --include '/root/***'  \
  --include '/home/***'   \
  --exclude '*'  \
  root@$MACHINE:// $DSTDIR/


# https://unix.stackexchange.com/questions/595411/why-rsync-doesnt-include-a-nested-directory


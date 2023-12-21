#!/usr/bin/env fish


rsync -av --progress -h   -e 'hpnssh -p 44' -r \
  --exclude 'dont_backup'  \
  --exclude 'venv' \
  --exclude '.cache'  \
  --exclude '__pycache__'  \
  --exclude '.npm'  \
  --exclude 'site-packages'  \
  --exclude 'node_modules'   \
  --exclude '/var/lib/docker/overlay2/'  \
  --exclude '/var/snap/docker/common/var-lib-docker/overlay2/'  \
  --exclude '/home/koom/go/'  \
  --include '/var/***' \
  --include '/etc/***'  \
  --include '/root/***'  \
  --include '/home/***'   \
  --exclude '*'  \
  root@vmi579006.contaboserver.net:// vmi579006_(date '+%F-%H-%M-%S')


# https://unix.stackexchange.com/questions/595411/why-rsync-doesnt-include-a-nested-directory
#  --include '/var/***' \


#!/usr/bin/env fish


rsync -av --progress -h   -e 'hpnssh -p 44' -r \
  --exclude 'dont_backup'  \
  --exclude 'venv' \
  --exclude '.cache'  \
  --exclude '__pycache__'  \
  --exclude '.npm'  \
  --exclude 'site-packages'  \
  --exclude 'node_modules'   \
--include "/var/www/***" \
--include '/var/lib/docker/volumes/***' \
--include '/var/log/***' \
--include '/var/lib/quassel/***' \
--include '/var/' \
  --exclude '*'     \
  root@vmi579006.contaboserver.net:// ~/backups/vmi579006_(date '+%F-%H-%M-%S')


# https://unix.stackexchange.com/questions/595411/why-rsync-doesnt-include-a-nested-directory
#  --include '/var/***' \
#  --include '/etc/***'  \
#  --include '/root/***'    \
#  --include '/home/***'   \


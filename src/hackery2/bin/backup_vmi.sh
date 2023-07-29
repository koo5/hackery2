#!/usr/bin/env fish
#(on r64)
#mkdir -p /bac4/backups/vmi
rsync -v -a -S -v --progress -r --delete -h  -e 'ssh -p 44'   --exclude 'dont_backup' --exclude 'venv' --exclude '.cache'  --exclude '__pycache__'  --exclude '.npm'  --exclude 'site-packages'  --exclude "node_modules"  --exclude "/home/sfi/ag/data"    --include "/home/***" --include "/var/www/***" --include "/etc/***" --include '/var/lib/docker/volumes/***' --include '/root/***' --include '/var/log/***'  --exclude "*"  root@vmi579006.contaboserver.net://  /bac4/backups/vmi/root_ext


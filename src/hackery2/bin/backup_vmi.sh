#!/usr/bin/env fish
mkdir -p /shared/backups/vmi
#rsync -av --progress -h   -e 'ssh -p 44' -r  --exclude 'dont_backup' --exclude 'venv' --exclude '.cache'  --exclude '__pycache__'  --exclude '.npm'  --exclude 'site-packages'  --exclude "node_modules"  --exclude "/home/sfi/ag/data" sfi@51.140.155.227://home/ ~/backups/(date '+%F-%H-%M-%S')
 rsync -av --progress -h   -e 'ssh -p 44' -r  --exclude 'dont_backup' --exclude 'venv' --exclude '.cache'  --exclude '__pycache__'  --exclude '.npm'  --exclude 'site-packages'  --exclude "node_modules"  --exclude "/home/sfi/ag/data" --include "/home/***" --include "/var/www/***" --include "/etc/***" --exclude "*" koom@vmi579006.contaboserver.net:// /shared/backups/vmi(date '+%F-%H-%M-%S')

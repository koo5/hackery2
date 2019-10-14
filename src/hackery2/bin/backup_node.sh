#!/usr/bin/env bash

rsync -av --progress -h   -e 'ssh -p 44' -r  --exclude dont_backup --exclude venv --exclude '.cache'  --exclude '__pycache__'  --exclude '.npm'  --exclude 'site-packages'  --exclude "node_modules"  sfi@51.140.155.227://home/ ~/backups/(date '+%F-%H-%M-%S')

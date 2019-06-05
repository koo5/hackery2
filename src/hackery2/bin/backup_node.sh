#!/usr/bin/env bash

rsync -av --progress -h   -e 'ssh' -r  --exclude '.cache'  --exclude '__pycache__' --exclude 'sfi/.local/lib' --exclude 'sfi/.npm' --exclude 'site-packages' --exclude 'node_modules' sfi@51.140.155.227://home/ /home/koom/backups/`date "+%F-%H-%M-%S"`

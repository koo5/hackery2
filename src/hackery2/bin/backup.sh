#!/usr/bin/env fish

cd (dirname (readlink -m (status --current-filename)))
set out ~/"Z_"(date -u '+%Y-%m-%d_%H-%M-%S')
PYTHONUNBUFFERED=1 python3 ./backup.py $argv | tee $out

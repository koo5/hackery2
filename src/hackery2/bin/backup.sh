#!/usr/bin/env fish

set out ~/"Z_"(date -u '+%Y-%m-%d_%H-%M-%S')
PYTHONUNBUFFERED=1 backup.py $argv | tee $out

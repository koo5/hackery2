#!/usr/bin/env fish

set out ~/"Z_"(date -u '+%Y-%m-%d_%H-%M-%S')
backup.py $argv | tee out

#!/usr/bin/env fish

set out ~/"backup_log_utc_"(date -u '+%Y-%m-%d_%H-%M-%S')
PYTHONUNBUFFERED=1 backup.py $argv | tee $out
cat out | grep \{\"result


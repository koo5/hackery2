#!/usr/bin/env fish

cd (dirname (readlink -m (status --current-filename)))
set out ~/"backup_log_utc_"(date -u '+%Y-%m-%d_%H-%M-%S')
PYTHONUNBUFFERED=1 backup $argv 2>&1 | tee $out
echo '------'
cat $out | grep \{\"result

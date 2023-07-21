#!/usr/bin/env bash

FN="sha1sum_`(date -u '+%Y-%m-%dT%H:%M:%SZ')`"
echo "sha1sum; fn; date -Ins; date -Ins -r" > $FN
find $@ \( -path /sys -o -path /proc -o -path /dev \) -prune -o -type f -exec md5sum "{}" \; -exec date -Ins \; -exec date -Ins -r "{}" \; >> $FN #2>&1
echo "done" >> $FN



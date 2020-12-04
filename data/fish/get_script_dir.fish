#!/usr/bin/env fish

set DIR (dirname (readlink -m (status --current-filename)))
echo $DIR
cd "$DIR"


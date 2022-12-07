#!/usr/bin/env fish

cd (dirname (readlink -m (status --current-filename)))

python3.9 ./ticker2.py

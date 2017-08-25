#!/usr/bin/env fish
cd (dirname (status -f))
pwd
. ../../../../env/bin/activate.fish
which python3
python3 ../snaploop.py 555 /home /snapshots_home

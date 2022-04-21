#!/usr/bin/env bash

export WORKDIR=/run/luks_integrity_benchmark
# crypto key
export KEY=key
# dev-mapper device name
export CRYPTDEV=luks_integrity_benchmark1

# dd
export DD_NOSYNC="dd "
export DD="$DD_NOSYNC conv=fsync "
export DD="$DD status=progress "

# sleep
export SLEEP=true
# sleep
export UPTIME_DELAY=true
# sleep 10

# block size that we will write/read
export BS=4096

# block count for image file
export BC=$(python3 -c "import os;print(int(round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 3 * 2 / int(os.environ['BS']))))")
#export BC=20000000
export  BC=20000000

# how much data should we actually try to read and write, this is better to be lower than the image size
export BCDATA=$(python3 -c "import os;print(int(round(int(os.environ['BC']) / 5 * 4)))")



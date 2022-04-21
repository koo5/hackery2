#!/usr/bin/env bash
set -e


# generate a key file
#dd status=none if=/dev/urandom bs=4096 count=1 of=$KEY


. ./settings.sh
./cleanup.sh
./init.sh
./benchmark.sh
./cleanup.sh

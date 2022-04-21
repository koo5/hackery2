#!/usr/bin/env bash
set -e


# generate a key file
#dd status=none if=/dev/urandom bs=4096 count=1 of=$KEY


. ./settings.sh
# where to mount ramfs
export MNT=$WORKDIR/ramfs
export DEV=$MNT/image.raw
./ramfs-cleanup.sh
./ramfs-init.sh
./benchmark.sh
./ramfs-cleanup.sh

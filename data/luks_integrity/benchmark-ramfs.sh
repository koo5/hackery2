#!/usr/bin/env bash
set -e


. ./settings.sh

# where to mount ramfs
export MNT=$WORKDIR/ramfs
export BENCHMARK_DEVICE=$MNT/image.raw

./ramfs-cleanup.sh
./ramfs-init.sh
./benchmark.sh
./ramfs-cleanup.sh

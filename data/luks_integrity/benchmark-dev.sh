#!/usr/bin/env bash
set -e

if [ -z "$BENCHMARK_DEVICE" ]; then
    echo "ERROR: BENCHMARK_DEVICE is not set."
    echo "Usage: BENCHMARK_DEVICE=/dev/sdX $0"
    exit 1
fi

if [ ! -e "$BENCHMARK_DEVICE" ]; then
    echo "ERROR: BENCHMARK_DEVICE=$BENCHMARK_DEVICE does not exist."
    exit 1
fi

echo "WARNING: This will DESTROY ALL DATA on $BENCHMARK_DEVICE"
read -p "Are you sure? [y/N] " answer
if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
    echo "Aborted."
    exit 1
fi

mkdir -p logs
. settings.sh
cryptsetup close $CRYPTDEV || true
cryptsetup close $CRYPTDEV2 || true
integritysetup close $CRYPTDEV || true
integritysetup close $CRYPTDEV2 || true
./benchmark.sh  |& tee logs/`date  '+%Y-%m-%dT%H:%M:%S'`

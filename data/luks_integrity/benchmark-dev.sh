#!/usr/bin/env bash
set -e

mkdir -p logs
. settings.sh
cryptsetup close $CRYPTDEV || true
cryptsetup close $CRYPTDEV2 || true
integritysetup close $CRYPTDEV || true
integritysetup close $CRYPTDEV2 || true
./benchmark.sh  |& tee logs/`date  '+%Y-%m-%dT%H:%M:%S'`

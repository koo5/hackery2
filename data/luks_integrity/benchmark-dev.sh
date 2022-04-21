#!/usr/bin/env bash
set -e

mkdir -p logs
. settings.sh
sudo ./benchmark.sh  |& tee logs/`date  '+%Y-%m-%dT%H:%M:%S'`

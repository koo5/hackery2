#!/usr/bin/env bash

export DROP_CACHES=./drop_caches.sh
export UPTIME=./uptime.sh

export WORKDIR=/run/luks_integrity_benchmark
# crypto key (auto-generated if missing)
export KEY=key
if [ ! -f "$KEY" ]; then
    dd status=none if=/dev/urandom bs=4096 count=1 of="$KEY"
fi
# dev-mapper device name
export CRYPTDEV=luks_integrity_benchmark1
export CRYPTDEV2=luks_integrity_benchmark2

# dd
export DD_NOSYNC="dd "
export DD="$DD_NOSYNC conv=fsync "
export DD="$DD status=progress "

# sleep
export SLEEP=sleep
export UPTIME_DELAY="sleep 1"
# sleep 10

# block size that we will write/read
export BS=4096

# block count for image file (override RAM percentage with BENCHMARK_RAM_PERCENT, default 67)
if [ -z "$BENCHMARK_RAM_PERCENT" ]; then
    export BENCHMARK_RAM_PERCENT=67
    _RAM_PERCENT_DEFAULT=1
fi
export BC=$(python3 -c "import os;pct=int(os.environ['BENCHMARK_RAM_PERCENT']);print(int(round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_AVPHYS_PAGES') * pct / 100 / int(os.environ['BS']))))")
echo "BC: $BC (${BENCHMARK_RAM_PERCENT}% of RAM)"

if [ -n "$_RAM_PERCENT_DEFAULT" ]; then
    IMAGE_SIZE=$(python3 -c "print(f'{int($BS) * int($BC) / 1024**3:.1f}')")
    AVAIL_MEM=$(python3 -c "import os; print(f'{os.sysconf(\"SC_PAGE_SIZE\") * os.sysconf(\"SC_AVPHYS_PAGES\") / 1024**3:.1f}')")
    echo "WARNING: This will use ~${IMAGE_SIZE}GB of RAM (${BENCHMARK_RAM_PERCENT}% of ${AVAIL_MEM}GB available)."
    echo "Override with BENCHMARK_RAM_PERCENT=<value>"
    read -p "Continue? [y/N] " answer
    if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

# results collection
export RESULTS_FILE=$(mktemp)
export BENCH_DD=./bench_dd.sh



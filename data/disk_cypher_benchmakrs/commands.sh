#!/usr/bin/env bash

export BENCHMARK_COMMANDS=./fio.sh
export BLOCK_DEVICE=/tmp/benchmark 

#mode: //
$BENCHMARK_COMMANDS


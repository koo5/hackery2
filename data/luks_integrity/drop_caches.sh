#!/usr/bin/env bash
set -e

sync
echo 3 > /proc/sys/vm/drop_caches

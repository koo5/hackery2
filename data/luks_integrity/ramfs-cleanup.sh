#!/usr/bin/env bash

echo "cleanup:"
./close.sh
rm $BENCHMARK_DEVICE || true
umount $MNT || true



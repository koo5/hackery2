#!/usr/bin/env bash

echo "cleanup:"
. ./settings.sh
./close.sh
rm $DEV || true
umount $MNT || true



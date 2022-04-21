#!/usr/bin/env bash

echo "cleanup:"
./close.sh
rm $DEV || true
umount $MNT || true



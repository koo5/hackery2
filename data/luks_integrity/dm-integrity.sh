#!/usr/bin/env bash

echo
echo
echo
echo "dm-integrity ..."

# clean the header
dd status=none if=/dev/zero bs=4096 count=10 of=$DEV  conv=notrunc


echo "YES" | integritysetup format $CYP $DEV
sh -x -c "integritysetup open $DEV $CRYPTDEV"
echo "writing..."
sh -x -c "$DD if=/dev/zero bs=$BS count=$BCDATA of=/dev/mapper/$CRYPTDEV"
sync; uptime; $UPTIME_DELAY
integritysetup close $CRYPTDEV

echo "reading it back:"
integritysetup   open   $DEV $CRYPTDEV
sh -x -c "$DD_NOSYNC  if=/dev/mapper/$CRYPTDEV bs=$BS count=$BCDATA of=/dev/null"
sync; uptime; $UPTIME_DELAY
integritysetup close $CRYPTDEV


echo
free -h | grep -v Swap


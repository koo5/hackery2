#!/usr/bin/env bash
set -e


. ./settings.sh


# clean the header
dd status=none if=/dev/zero bs=4096 count=10 of=$DEV  conv=notrunc


echo
echo "formatting with luks2  $CYP  ..."
echo "YES" | sh -c "cryptsetup --key-file  key  luksFormat --type luks2    $CYP   $DEV "
sync
cryptsetup --key-file  key   open   $DEV $CRYPTDEV

echo "writing  ..."
sh -c "$DD if=/dev/zero bs=$BS count=$BCDATA of=/dev/mapper/$CRYPTDEV"
sync
cryptsetup close $CRYPTDEV

echo "reading it back:"
sync
cryptsetup --key-file  key  open   $DEV  $CRYPTDEV
sync
sh -c "$DD if=/dev/mapper/$CRYPTDEV bs=$BS count=$BCDATA of=/dev/null"
sync
cryptsetup close $CRYPTDEV


echo
free -h | grep -v Swap

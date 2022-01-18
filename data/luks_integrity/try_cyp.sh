#!/usr/bin/env bash
set -e


. ./settings.sh


# clean the header
dd status=none if=/dev/zero bs=4096 count=10 of=$DEV  conv=notrunc


echo
echo "formatting with luks2  $CYP  ..."
echo "YES" | sh -x -c "cryptsetup --key-file  key  luksFormat --type luks2    $CYP   $DEV "
sync; sleep 10

cryptsetup --key-file  key   open   $DEV $CRYPTDEV
sync; sleep 10

echo "writing  ..."
sh -x -c "$DD if=/dev/zero bs=$BS count=$BCDATA of=/dev/mapper/$CRYPTDEV"
sync; sleep 10; uptime
cryptsetup close $CRYPTDEV

echo "reading it back:"
sync; sleep 10
cryptsetup --key-file  key  open   $DEV  $CRYPTDEV
sync; sleep 10

sh -x -c "$DD if=/dev/mapper/$CRYPTDEV bs=$BS count=$BCDATA of=/dev/null"
sync; sleep 10

uptime
cryptsetup close $CRYPTDEV


echo
free -h | grep -v Swap

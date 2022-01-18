#!/usr/bin/env bash
set -e


. ./settings.sh


# clean the header
dd status=none if=/dev/zero bs=4096 count=10 of=$DEV  conv=notrunc


echo
echo "formatting with luks2  $CYP  ..."
sh -c "cryptsetup --key-file  key  luksFormat -vq --type luks2    "$CYP"   $DEV"
cryptsetup --key-file  key   open   $DEV $CRYPTDEV

echo "writing  ..."
sh -c "$DD if=/dev/zero bs=$BS count=$BCDATA of=/dev/mapper/$CRYPTDEV"
cryptsetup close $CRYPTDEV

echo "reading it back:"
cryptsetup --key-file  key  open   $DEV  $CRYPTDEV
sh -c "$DD if=/dev/mapper/$CRYPTDEV bs=$BS count=$BCDATA of=/dev/null"
cryptsetup close $CRYPTDEV


echo
free -h | grep -v Swap

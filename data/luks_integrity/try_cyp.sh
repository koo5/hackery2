#!/usr/bin/env bash
set -e

echo
echo
echo
echo
echo
echo
echo "luks2  $CYP  ..."

# clean the header
dd status=none if=/dev/zero bs=4096 count=10 of=$DEV  conv=notrunc


echo
echo "YES" | sh -x -c "cryptsetup --key-file  $KEY  luksFormat --type luks2    $CYP   $DEV "
sync; $UPTIME_DELAY

cryptsetup --key-file  $KEY   open   $DEV $CRYPTDEV
sync; $UPTIME_DELAY

echo "writing  ..."
sh -x -c "$DD if=/dev/zero bs=$BS count=$BCDATA of=/dev/mapper/$CRYPTDEV"
sync
$UPTIME
cryptsetup close $CRYPTDEV

$DROP_CACHES

echo "reading it back:"
sync; $UPTIME_DELAY
cryptsetup --key-file  $KEY  open   $DEV  $CRYPTDEV
sync; $UPTIME_DELAY

sh -x -c "$DD_NOSYNC if=/dev/mapper/$CRYPTDEV bs=$BS count=$BCDATA of=/dev/null"
sync
$UPTIME


cryptsetup close $CRYPTDEV

sync; $UPTIME_DELAY
echo
free -h | grep -v Swap

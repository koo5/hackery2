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
dd status=none if=/dev/zero bs=4096 count=10 of=$BENCHMARK_DEVICE  conv=notrunc


echo
echo "YES" | sh -x -c "cryptsetup --key-file  $KEY  luksFormat --type luks2    $CYP   $BENCHMARK_DEVICE "
sync; $UPTIME_DELAY

cryptsetup --key-file  $KEY   open   $BENCHMARK_DEVICE $CRYPTDEV
sync; $UPTIME_DELAY
DEV_BLOCKS=$(($(blockdev --getsize64 /dev/mapper/$CRYPTDEV) / BS))

echo "writing  ..."
$BENCH_DD "luks2 $CYP write" $DD if=/dev/zero bs=$BS count=$DEV_BLOCKS of=/dev/mapper/$CRYPTDEV
sync
$UPTIME
cryptsetup close $CRYPTDEV

$DROP_CACHES

echo "reading it back:"
sync; $UPTIME_DELAY
cryptsetup --key-file  $KEY  open   $BENCHMARK_DEVICE  $CRYPTDEV
sync; $UPTIME_DELAY
DEV_BLOCKS=$(($(blockdev --getsize64 /dev/mapper/$CRYPTDEV) / BS))

$BENCH_DD "luks2 $CYP read" $DD_NOSYNC if=/dev/mapper/$CRYPTDEV bs=$BS count=$DEV_BLOCKS of=/dev/null
sync
$UPTIME


cryptsetup close $CRYPTDEV

sync; $UPTIME_DELAY
echo
free -h | grep -v Swap

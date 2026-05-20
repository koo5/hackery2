#!/usr/bin/env bash
set -e

echo
echo
echo
echo
echo
echo
echo "luks inside dm-integrity ..."


# clean the header
dd status=none if=/dev/zero bs=4096 count=10 of=$BENCHMARK_DEVICE  conv=notrunc


echo "YES" | integritysetup format $INTEGRITY_CYP $BENCHMARK_DEVICE
sh -x -c "integritysetup open $BENCHMARK_DEVICE $CRYPTDEV"
udevadm settle
sync; $SLEEP 1

echo
echo "formatting with luks2  $CYP  ..."
echo "YES" | sh -x -c "cryptsetup --key-file  $KEY  luksFormat --type luks2   $CYP   /dev/mapper/$CRYPTDEV "
sync; $SLEEP 1
cryptsetup --key-file  $KEY   open   /dev/mapper/$CRYPTDEV $CRYPTDEV2
sync; $UPTIME_DELAY
DEV_BLOCKS=$(($(blockdev --getsize64 /dev/mapper/$CRYPTDEV2) / BS))

echo "writing..."
$BENCH_DD "luks2+dm-integrity $INTEGRITY_CYP write" $DD if=/dev/zero bs=$BS count=$DEV_BLOCKS of=/dev/mapper/$CRYPTDEV2
sync
$UPTIME
cryptsetup close $CRYPTDEV2
integritysetup close $CRYPTDEV

$DROP_CACHES

echo "reading it back:"
integritysetup   open   $BENCHMARK_DEVICE $CRYPTDEV
udevadm settle
cryptsetup --key-file  $KEY   open   /dev/mapper/$CRYPTDEV $CRYPTDEV2
DEV_BLOCKS=$(($(blockdev --getsize64 /dev/mapper/$CRYPTDEV2) / BS))
$BENCH_DD "luks2+dm-integrity $INTEGRITY_CYP read" $DD_NOSYNC if=/dev/mapper/$CRYPTDEV2 bs=$BS count=$DEV_BLOCKS of=/dev/null
sync
$UPTIME
cryptsetup close $CRYPTDEV2
integritysetup close $CRYPTDEV


echo
free -h | grep -v Swap

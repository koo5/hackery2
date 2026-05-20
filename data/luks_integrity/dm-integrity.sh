#!/usr/bin/env bash

echo
echo
echo
echo
echo
echo
echo "dm-integrity ..."

# clean the header
dd status=none if=/dev/zero bs=4096 count=10 of=$BENCHMARK_DEVICE  conv=notrunc


echo "YES" | integritysetup format $CYP $BENCHMARK_DEVICE
sh -x -c "integritysetup open $BENCHMARK_DEVICE $CRYPTDEV"
DEV_BLOCKS=$(($(blockdev --getsize64 /dev/mapper/$CRYPTDEV) / BS))

echo
echo "writing..."
$BENCH_DD "dm-integrity $CYP write" $DD if=/dev/zero bs=$BS count=$DEV_BLOCKS of=/dev/mapper/$CRYPTDEV
echo
sync
$UPTIME
$DROP_CACHES
sleep 5
integritysetup close $CRYPTDEV
$DROP_CACHES


echo
echo "reading it back:"
integritysetup   open   $BENCHMARK_DEVICE $CRYPTDEV
DEV_BLOCKS=$(($(blockdev --getsize64 /dev/mapper/$CRYPTDEV) / BS))
$BENCH_DD "dm-integrity $CYP read" $DD_NOSYNC if=/dev/mapper/$CRYPTDEV bs=$BS count=$DEV_BLOCKS of=/dev/null
echo
sync
$UPTIME
sleep 5
integritysetup close $CRYPTDEV


echo
free -h | grep -v Swap


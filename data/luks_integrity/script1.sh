#!/usr/bin/env bash
set -e


# generate a key file
dd status=none if=/dev/urandom bs=4096 count=1 of=key


./cleanup.sh
. ./settings.sh
./init.sh


echo
free -h | grep -v Swap




echo
echo "raw write to ramfs:"
sh -x -c "$DD if=/dev/zero bs=$BS count=$BC of=$DEV"
sync; uptime; sleep 10
echo "reading it back:"
sh -x -c "$DD if=$DEV bs=$BS count=$BC of=/dev/null"
sync; uptime; sleep 10





echo
free -h | grep -v Swap





echo
echo "dm-integrity ..."

echo "YES" | integritysetup format $DEV 
sh -x -c "integritysetup open $DEV $CRYPTDEV"
echo "writing..."
sh -x -c "$DD if=/dev/zero bs=$BS count=$BCDATA of=/dev/mapper/$CRYPTDEV"
sync; uptime; sleep 10
integritysetup close $CRYPTDEV

echo "reading it back:"
integritysetup   open   $DEV $CRYPTDEV
sh -x -c "$DD  if=/dev/mapper/$CRYPTDEV bs=$BS count=$BCDATA of=/dev/null"
sync; uptime; sleep 10
integritysetup close $CRYPTDEV


echo
free -h | grep -v Swap




export CYP=""
./try_cyp.sh
export CYP="--integrity hmac-sha1"
./try_cyp.sh
export CYP="--integrity hmac-sha256"
./try_cyp.sh
export CYP=" --cipher=chacha20-random  --integrity=poly1305"
./try_cyp.sh






echo
echo "luks inside dm-integrity ..."
export CYP=""

echo "YES" | integritysetup format $DEV
sh -x -c "integritysetup open $DEV $CRYPTDEV"
sync; sleep 1

echo
echo "formatting with luks2  $CYP  ..."
echo "YES" | sh -x -c "cryptsetup --key-file  key  luksFormat --type luks2   $CYP   /dev/mapper/$CRYPTDEV "
sync; sleep 1
cryptsetup --key-file  key   open   /dev/mapper/$CRYPTDEV $CRYPTDEV-2
sync; sleep 10

echo "writing..."
sh -x -c "$DD if=/dev/zero bs=$BS count=$BCDATA of=/dev/mapper/$CRYPTDEV-2"
sync; uptime; sleep 10
cryptsetup close $CRYPTDEV-2
integritysetup close $CRYPTDEV

echo "reading it back:"
integritysetup   open   $DEV $CRYPTDEV
cryptsetup --key-file  key   open   /dev/mapper/$CRYPTDEV $CRYPTDEV-2
sh -x -c "$DD  if=/dev/mapper/$CRYPTDEV-2 bs=$BS count=$BCDATA of=/dev/null"
sync; uptime; sleep 10
cryptsetup close $CRYPTDEV-2
integritysetup close $CRYPTDEV


echo
free -h | grep -v Swap


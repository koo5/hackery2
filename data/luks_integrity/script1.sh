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


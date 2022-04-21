#!/usr/bin/env bash
set -e



echo
free -h | grep -v Swap || true



echo
echo
echo
echo "raw write:"
sh -x -c "$DD if=/dev/zero bs=$BS count=$BC of=$DEV"
sync; uptime; $UPTIME_DELAY
echo
echo
echo
echo "reading it back:"
sh -x -c "$DD_NOSYNC if=$DEV bs=$BS count=$BC of=/dev/null"
sync; uptime; $UPTIME_DELAY


echo
free -h | grep -v Swap || true



export CYP="--integrity crc32c"
./dm-integrity.sh

export CYP="--integrity sha1"
./dm-integrity.sh

export CYP="--integrity sha256"
./dm-integrity.sh



echo
free -h | grep -v Swap || true



export CYP=""
./try_cyp.sh

export CYP="--integrity hmac-sha1"
./try_cyp.sh

export CYP="--integrity hmac-sha256"
./try_cyp.sh

export CYP=" --cipher=chacha20-random  --integrity=poly1305"
./try_cyp.sh

export CYP="--integrity crc32c"
./luks_inside_dm-integrity.sh

export CYP="--integrity sha1"
./luks_inside_dm-integrity.sh

export CYP="--integrity sha256"
./luks_inside_dm-integrity.sh




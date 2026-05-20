#!/usr/bin/env bash
set -e



echo
free -h | grep -v Swap || true



echo
echo
echo
echo "raw write:"
$BENCH_DD "raw write" $DD if=/dev/zero bs=$BS count=$BC of=$BENCHMARK_DEVICE
sync
$UPTIME
echo
echo
$DROP_CACHES
echo
echo "raw read:"
$BENCH_DD "raw read" $DD_NOSYNC if=$BENCHMARK_DEVICE bs=$BS count=$BC of=/dev/null
sync
$UPTIME


echo;echo;echo;echo;
free -h | grep -v Swap || true

echo "DM-INTEGRITY"

export CYP="--integrity crc32c"
./dm-integrity.sh

export CYP="--integrity sha1"
./dm-integrity.sh

export CYP="--integrity sha256"
./dm-integrity.sh



echo;echo;echo;echo;
free -h | grep -v Swap || true

echo "LUKS2"

export CYP=""
./try_cyp.sh

export CYP="--integrity hmac-sha1"
./try_cyp.sh

export CYP="--integrity hmac-sha256"
./try_cyp.sh

export CYP=" --cipher=chacha20-random  --integrity=poly1305"
./try_cyp.sh

#echo;echo;echo;echo;
#echo "LUKS INSIDE DM-INTEGRITY"
#
#export CYP=""
#
#export INTEGRITY_CYP="--integrity crc32c"
#./luks_inside_dm-integrity.sh
#
#export INTEGRITY_CYP="--integrity sha1"
#./luks_inside_dm-integrity.sh
#
#export INTEGRITY_CYP="--integrity sha256"
#./luks_inside_dm-integrity.sh


echo;echo;echo
echo "=== BENCHMARK RESULTS ==="
echo "Test|Speed" | cat - "$RESULTS_FILE" | column -t -s'|'



echo
echo
echo
echo "luks inside dm-integrity ..."


# clean the header
dd status=none if=/dev/zero bs=4096 count=10 of=$DEV  conv=notrunc


echo "YES" | integritysetup format $INTEGRITY_CYP $DEV
sh -x -c "integritysetup open $DEV $CRYPTDEV"
sync; $SLEEP 1

echo
echo "formatting with luks2  $CYP  ..."
echo "YES" | sh -x -c "cryptsetup --key-file  $KEY  luksFormat --type luks2   $CYP   /dev/mapper/$CRYPTDEV "
sync; $SLEEP 1
cryptsetup --key-file  $KEY   open   /dev/mapper/$CRYPTDEV $CRYPTDEV2
sync; $UPTIME_DELAY

echo "writing..."
sh -x -c "$DD if=/dev/zero bs=$BS count=$BCDATA of=/dev/mapper/$CRYPTDEV2"
sync
$UPTIME
cryptsetup close $CRYPTDEV2
integritysetup close $CRYPTDEV

$DROP_CACHES

echo "reading it back:"
integritysetup   open   $DEV $CRYPTDEV
cryptsetup --key-file  $KEY   open   /dev/mapper/$CRYPTDEV $CRYPTDEV2
sh -x -c "$DD_NOSYNC  if=/dev/mapper/$CRYPTDEV2 bs=$BS count=$BCDATA of=/dev/null"
sync
$UPTIME
cryptsetup close $CRYPTDEV2
integritysetup close $CRYPTDEV


echo
free -h | grep -v Swap

#!/usr/bin/env fish
export DST=bac1

mount | grep /bac4;  \
and  mount | grep $DST ; \
and bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/bac4  commit_and_push_and_checkout   --SUBVOLUME=/bac4/cold --REMOTE_SUBVOLUME=/$DST/cold/

mount | grep $DST ; \
and bfg  --YES=true  --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push_and_checkout    --SUBVOLUME=/d    --REMOTE_SUBVOLUME=/$DST/lean

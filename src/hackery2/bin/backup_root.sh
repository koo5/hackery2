#!/usr/bin/env fish

bfg  --YES=true  --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push_and_checkout    --SUBVOLUME=/    --REMOTE_SUBVOLUME=/$DST/r6_root

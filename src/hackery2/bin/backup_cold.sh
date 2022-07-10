#!/usr/bin/env fish

mount | grep /bac4;  \
and bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/bac4  commit_and_push_and_checkout   --SUBVOLUME=/bac4/cold --REMOTE_SUBVOLUME=/$DST/cold/

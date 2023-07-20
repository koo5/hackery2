#!/usr/bin/env fish

# bac4 -> bac7

mount | grep bac4 > /dev/null; and mount | grep bac7 > /dev/null; and \
bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/bac4  commit_and_push_and_checkout   --SUBVOLUME=/bac4/cold --REMOTE_SUBVOLUME=/bac7/cold/

# nb -> bac7

mount | grep bac7 > /dev/null; and \
bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push_and_checkout   --SUBVOLUME=/d --REMOTE_SUBVOLUME=/bac7/lean/

mount | grep bac7 > /dev/null; and \
bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push_and_checkout   --SUBVOLUME=/home --REMOTE_SUBVOLUME=/bac7/r6_home

mount | grep bac7 > /dev/null; and \
bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push_and_checkout   --SUBVOLUME=/ --REMOTE_SUBVOLUME=/bac7/r6_root

# nb -> bac4

mount | grep bac4 > /dev/null; and \
bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push_and_checkout   --SUBVOLUME=/d --REMOTE_SUBVOLUME=/bac4/lean/

mount | grep bac4 > /dev/null; and \
bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push_and_checkout   --SUBVOLUME=/home --REMOTE_SUBVOLUME=/bac4/r6_home/

mount | grep bac4 > /dev/null; and \
bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push_and_checkout   --SUBVOLUME=/ --REMOTE_SUBVOLUME=/bac4/r6_root/


# nb -> hp

ping -c 1 -W 3 10.0.0.20; and  bfg  --YES=true   --sshstr='/opt/hpnssh/usr/bin/ssh   -p 2222   -o TCPRcvBufPoll=yes -o NoneSwitch=yes  -o NoneEnabled=yes     koom@10.0.0.20'    --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/nvme0n1p6_crypt_root  commit_and_push    --SUBVOLUME=/d --REMOTE_SUBVOLUME=/mx500data/lean


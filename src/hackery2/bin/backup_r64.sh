#!/usr/bin/env fish

sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"

# todo cold


mount | grep bac4; and sudo rsync -v -a -S -v --progress -r --delete /home /root /etc /var/www /var/lib/docker/volumes /var/lib/snapd     /bac4/backup_r64_ext


# bind mount, for transactionally ensuring correct target fs?


#mount | grep $DEST; and 
bfg --YES=true --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/d0/  commit_and_push_and_checkout   --SUBVOLUME=/d0 --REMOTE_SUBVOLUME=$DEST/backup_r64_d0
#mount | grep $DEST; and 
bfg --YES=true --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/bac4/  commit_and_push_and_checkout   --SUBVOLUME=/bac4/lean --REMOTE_SUBVOLUME=$DEST/backup_r64_lean
#mount | grep $DEST; and
bfg --YES=true --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/bac4/  commit_and_push_and_checkout   --SUBVOLUME=/bac4/backup_r64_ext --REMOTE_SUBVOLUME=$DEST/backup_r64_ext

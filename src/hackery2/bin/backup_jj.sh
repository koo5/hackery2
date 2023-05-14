#!/usr/bin/env fish

sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"
sudo rsync -v -a -S -v --progress -r --delete /home /root /etc /var/www /var/lib/docker/volumes /var/lib/snapd    /d1/backup/jj_ext | tee ~/backup_log1
#mount | grep bac16; and  bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/d1/  commit_and_push_and_checkout   --SUBVOLUME=/d1/backup/jj_ext --REMOTE_SUBVOLUME=/bac16/backup_jj_ext

mount | grep bac16; and  bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/d1/  commit_and_push_and_checkout   --SUBVOLUME=/d1/images --REMOTE_SUBVOLUME=/bac16/backup_jj_images

mount | grep bac16; and  bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/d1/  commit_and_push_and_checkout   --SUBVOLUME=/d1/ --REMOTE_SUBVOLUME=/bac16/backup_jj_d1


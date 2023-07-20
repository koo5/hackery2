#!/usr/bin/env fish

sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"
sudo rsync -v -a -S -v --progress -r --delete /root /etc /var/www /var/lib/docker/volumes     /mx500data/backup_hp_ext
mount | grep bac16; and  bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/mx500data/  commit_and_push_and_checkout   --SUBVOLUME=/mx500data/backup_hp_ext --REMOTE_SUBVOLUME=/bac16/backup_hp_ext
mount | grep bac16; and  bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/mx500data/  commit_and_push_and_checkout   --SUBVOLUME=/mx500data/home --REMOTE_SUBVOLUME=/bac16/backup_hp_home
mount | grep bac16; and  bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/mx500data/  commit_and_push_and_checkout   --SUBVOLUME=/mx500data/lean --REMOTE_SUBVOLUME=/bac16/backup_hp_lean
mount | grep bac16; and  bfg  --YES=true   --LOCAL_FS_TOP_LEVEL_SUBVOL_MOUNT_POINT=/mx500data/  commit_and_push_and_checkout   --SUBVOLUME=/mx500data/leanpriv --REMOTE_SUBVOLUME=/bac16/backup_hp_leanpriv



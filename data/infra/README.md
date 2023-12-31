# backup infrastructure
Machine r64 is the backup server. It has a big btrfs disk where the bulk of my data lives, divided into subvolumes.
Each machine also has a small ext4 or btrfs disk where the OS lives.
We rsync ext4 disks into a subvolume on the btrfs disk, and then use bfg to transfer the btrfs subvolumes.
But maybe in future we should just rsync them to the target btrfs filesystem directly.

## steps

### Start up the backup server. 
Keyboard has to be plugged in and password entered.

### Mount all connected disks:
```
sudo swipl -s /home/koom/hackery2/src/hackery2/bin/disks.pl  -g "start"
```

### run plain `backup.sh` on all other machines,
.., updating the `/bac4/backups` folder on r64, and then run `backup.sh` on r64, updating the `/bac9/backups` folder on bac9. Bac9 is now ready to be taken off-site.


## philosophy
the doubled-up bac9 easily takes all the data, and so does the bac4, which has the master copy.

### The simplest approach..
 ..therefore is to first run plain `backup.sh` on all other machines, updating the `/bac4/backups` folder on r64, and then run `backup.sh` on r64, updating the `/bac9/backups` folder on bac9. 

### It's also possible to..
explicitly transfer directly to the backup disk like so:
```
backup.sh --target_machine='r64' --target_fs=/bac9
```
But if a machine is backed up to both the primary copy and the backup copy, this in effect creates two branches of snapshots on the backup disk, taking up twice as much space and bandwidth. This should eventually be resolved inside BFG. BFG should be made to take into account the snapshots that were created before (and transferred onto a different filesystem than the current target one), and should create and send a series of snapshots. This is in line in making it "a git-like workflow for btrfs." 


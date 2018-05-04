sudo cryptsetup open  /dev/sdb1 bbb
sudo partprobe
sudo swapoff -a
sudo swapon -p 10 /dev/mapper/bbb1 
sudo swapon -p 10 /dev/dm-*
sudo mount /dev/sda1 /mnt/500/
sudo mount /dev/mapper/bbb2 /mnt/intel500/

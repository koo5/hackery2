#sudo cryptsetup open  /dev/sdb1 bbb
sudo cryptsetup open /dev/sdb1 sdb1
sudo cryptsetup open /dev/sdc2 sdc2
sudo cryptsetup open /dev/sdb2 sdb2
sudo mount /dev/mapper/sdb2  /mnt/sdb2
sudo swapoff -a
sudo swapon -p 10 /dev/mapper/luks-7dec246c-33a0-4bbc-b103-415c7f5815c7
sudo swapon -p 10 /dev/dm-*
sudo swapon -s

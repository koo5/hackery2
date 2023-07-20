#!/usr/bin/env fish

echo "10.0.7.64..."
sudo sshfs -p22 root@10.0.7.64:// /mnt/r64; and exit 0
echo "192.168.8.64..."
sudo sshfs -p22 root@192.168.8.64:// /mnt/r64/
echo "aight"

#!/usr/bin/env fish
mkdir -p /var/swaps
set vm $argv[1]
set file /var/swaps/$vm.swap.raw
qemu-img create -f raw $file 30g
chmod 0600 $file
mkswap -L swap $file


#!/usr/bin/env fish

set vm $argv[1]
set file /r3/guest_swaps/$vm.swap.raw
qemu-img create -f raw $file 30g
chmod 0600 $file
mkswap $file


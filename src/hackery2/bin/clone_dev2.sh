#!/usr/bin/env fish

set suffix $argv[1]; 
set p /d/images/clones
mkdir $p
begin 
	true

	and rm -f $p/dev2-$suffix.raw;
	and rm -f $p/dev2-btrfs-$suffix.raw;

	and qemu-img create -f raw /r3/guest_swaps/dev2-$suffix.swap.raw 20G; 
	and chmod 0600 /r3/guest_swaps/dev2-$suffix.swap.raw; 
	and mkswap /r3/guest_swaps/dev2-$suffix.swap.raw; 
	
	
	#and cp --reflink /d/images/dev2.raw /d/images/dev2-$suffix.raw; and 
	#cp --reflink /d/images/dev2-btrfs.raw /d/images/dev2-btrfs-$suffix.raw; and
	
	and virt-clone --reflink  -o  dev2 -n dev2-$suffix --file  $p/dev2-$suffix.raw  --file $p/dev2-btrfs-$suffix.raw   --skip-copy vdb #--file /r3/guest_swaps/dev2-$suffix.swap.raw
	
	and echo "now manually set the new vm to use /r3/guest_swaps/dev2-$suffix.swap.raw'
	
	true
end

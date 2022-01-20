# luks / dm-crypt / dm-integrity ciphers benchmark. Reading from/writing to a ramfs mount.

## test machine: Ryzen 9 5900X 12-Core

```
root@r6 /d/h/d/luks_integrity (master)# ./script1.sh
cleanup:
Device luks_integrity_benchmark1 is not active.

               total        used        free      shared  buff/cache   available
Mem:           125Gi       5,6Gi       114Gi       157Mi       5,3Gi       118Gi

raw write to ramfs:
+ dd if=/dev/zero bs=4096 count=21970829 of=/run/luks_integrity_benchmark/ramfs/image.raw
21970829+0 records in
21970829+0 records out
89992515584 bytes (90 GB, 84 GiB) copied, 22,2362 s, 4,0 GB/s
 01:04:03 up  2:11,  3 users,  load average: 0,61, 0,53, 2,01
reading it back:
+ dd if=/run/luks_integrity_benchmark/ramfs/image.raw bs=4096 count=21970829 of=/dev/null
21970829+0 records in
21970829+0 records out
89992515584 bytes (90 GB, 84 GiB) copied, 10,9433 s, 8,2 GB/s
 01:04:25 up  2:11,  3 users,  load average: 0,59, 0,53, 1,97

               total        used        free      shared  buff/cache   available
Mem:           125Gi       5,7Gi        30Gi       157Mi        89Gi        34Gi

dm-integrity ...
Formatted with tag size 4, internal integrity crc32c.
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 00:19.042, 85094 MiB written, speed   4,4 GiB/s
+ integritysetup open /run/luks_integrity_benchmark/ramfs/image.raw luks_integrity_benchmark1
writing...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 56,0631 s, 1,3 GB/s
 01:05:50 up  2:13,  3 users,  load average: 4,07, 1,56, 2,20
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 33,4702 s, 2,2 GB/s
 01:06:34 up  2:13,  3 users,  load average: 2,87, 1,58, 2,18

               total        used        free      shared  buff/cache   available
Mem:           125Gi       5,8Gi        31Gi       155Mi        88Gi        34Gi

formatting with luks2    ...
+ cryptsetup --key-file key luksFormat --type luks2 /run/luks_integrity_benchmark/ramfs/image.raw
writing  ...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 49,0927 s, 1,5 GB/s
 01:08:15 up  2:15,  3 users,  load average: 13,84, 5,24, 3,38
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 39,0071 s, 1,8 GB/s
 01:09:26 up  2:16,  3 users,  load average: 5,05, 4,42, 3,24

               total        used        free      shared  buff/cache   available
Mem:           125Gi       5,9Gi        31Gi       155Mi        88Gi        34Gi

formatting with luks2  --integrity hmac-sha1  ...
+ cryptsetup --key-file key luksFormat --type luks2 --integrity hmac-sha1 /run/luks_integrity_benchmark/ramfs/image.raw
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 04:16.914, 82519 MiB written, speed 321,2 MiB/s
writing  ...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 80,0923 s, 899 MB/s
 01:15:54 up  2:23,  3 users,  load average: 18,36, 8,97, 5,12
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 134,665 s, 535 MB/s
 01:18:41 up  2:25,  3 users,  load average: 3,38, 6,16, 4,66

               total        used        free      shared  buff/cache   available
Mem:           125Gi       6,0Gi        31Gi       152Mi        88Gi        34Gi

formatting with luks2  --integrity hmac-sha256  ...
+ cryptsetup --key-file key luksFormat --type luks2 --integrity hmac-sha256 /run/luks_integrity_benchmark/ramfs/image.raw
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 07:11.878, 80699 MiB written, speed 186,9 MiB/s
writing  ...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 78,7401 s, 914 MB/s
 01:28:03 up  2:35,  3 users,  load average: 17,53, 8,72, 5,69
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 213,055 s, 338 MB/s
 01:32:09 up  2:39,  3 users,  load average: 3,03, 5,60, 5,10

               total        used        free      shared  buff/cache   available
Mem:           125Gi       6,4Gi        30Gi       193Mi        88Gi        34Gi

formatting with luks2   --cipher=chacha20-random  --integrity=poly1305  ...
+ cryptsetup --key-file key luksFormat --type luks2 --cipher=chacha20-random --integrity=poly1305 /run/luks_integrity_benchmark/ramfs/image.raw
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 04:18.559, 81296 MiB written, speed 314,4 MiB/s
writing  ...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 110,108 s, 654 MB/s
 01:39:17 up  2:46,  3 users,  load average: 25,68, 13,50, 8,03
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 123,322 s, 584 MB/s
 01:41:52 up  2:49,  3 users,  load average: 4,82, 9,28, 7,26

               total        used        free      shared  buff/cache   available
Mem:           125Gi       6,3Gi        30Gi       143Mi        88Gi        34Gi

luks inside dm-integrity ...
WARNING: Device /run/luks_integrity_benchmark/ramfs/image.raw already contains a 'crypto_LUKS' superblock signature.
Formatted with tag size 4, internal integrity crc32c.
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 00:18.976, 85094 MiB written, speed   4,4 GiB/s
+ integritysetup open /run/luks_integrity_benchmark/ramfs/image.raw luks_integrity_benchmark1

formatting with luks2    ...
+ cryptsetup --key-file key luksFormat --type luks2 /dev/mapper/luks_integrity_benchmark1
writing...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1-2
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 72,346 s, 995 MB/s
 01:43:59 up  2:51,  3 users,  load average: 21,25, 12,71, 8,67
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1-2 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 45,8612 s, 1,6 GB/s
 01:44:57 up  2:52,  3 users,  load average: 9,96, 10,97, 8,31


```

# todo
* allow to specify a real block device
* output CSV or similar




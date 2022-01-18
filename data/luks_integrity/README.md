# luks / dm-crypt / dm-integrity ciphers benchmark. Reading from/writing to a ramfs mount.

## test machine: Ryzen 9 5900X 12-Core

```

root@r6 /d/h/d/luks_integrity (master) [2]# ./script1.sh
cleanup:
Device luks_integrity_benchmark1 is not active.

               total        used        free      shared  buff/cache   available
Mem:           125Gi       6,3Gi       110Gi       248Mi       9,1Gi       118Gi

raw write to ramfs:
+ dd if=/dev/zero bs=4096 count=21970829 of=/run/luks_integrity_benchmark/ramfs/image.raw
21970829+0 records in
21970829+0 records out
89992515584 bytes (90 GB, 84 GiB) copied, 22,8169 s, 3,9 GB/s
 00:04:52 up  1:12,  3 users,  load average: 2,66, 2,49, 2,38
reading it back:
+ dd if=/run/luks_integrity_benchmark/ramfs/image.raw bs=4096 count=21970829 of=/dev/null
21970829+0 records in
21970829+0 records out
89992515584 bytes (90 GB, 84 GiB) copied, 11,1858 s, 8,0 GB/s
 00:05:13 up  1:12,  3 users,  load average: 2,96, 2,58, 2,41

               total        used        free      shared  buff/cache   available
Mem:           125Gi       6,5Gi        25Gi       268Mi        93Gi        33Gi

dm-integrity ...
Formatted with tag size 4, internal integrity crc32c.
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 00:19.353, 85094 MiB written, speed   4,3 GiB/s
+ integritysetup open /run/luks_integrity_benchmark/ramfs/image.raw luks_integrity_benchmark1
writing...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 58,2157 s, 1,2 GB/s
 00:06:41 up  1:13,  3 users,  load average: 7,46, 4,01, 2,93
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 34,4741 s, 2,1 GB/s
 00:07:26 up  1:14,  3 users,  load average: 25,46, 8,54, 4,47

               total        used        free      shared  buff/cache   available
Mem:           125Gi       4,7Gi        32Gi       121Mi        88Gi        35Gi

formatting with luks2    ...
+ cryptsetup --key-file key luksFormat --type luks2 /run/luks_integrity_benchmark/ramfs/image.raw
writing  ...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 47,543 s, 1,5 GB/s
 00:09:06 up  1:16,  3 users,  load average: 18,96, 10,97, 5,75
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 37,9745 s, 1,9 GB/s
 00:10:16 up  1:17,  3 users,  load average: 6,89, 8,97, 5,43

               total        used        free      shared  buff/cache   available
Mem:           125Gi       4,6Gi        32Gi       113Mi        88Gi        36Gi

formatting with luks2  --integrity hmac-sha1  ...
+ cryptsetup --key-file key luksFormat --type luks2 --integrity hmac-sha1 /run/luks_integrity_benchmark/ramfs/image.raw
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 04:16.996, 82519 MiB written, speed 321,1 MiB/s
writing  ...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 76,7463 s, 938 MB/s
 00:16:31 up  1:23,  3 users,  load average: 17,11, 9,60, 6,31
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 133,432 s, 540 MB/s
 00:19:17 up  1:26,  3 users,  load average: 3,34, 6,57, 5,67

               total        used        free      shared  buff/cache   available
Mem:           125Gi       5,0Gi        32Gi       117Mi        88Gi        35Gi

formatting with luks2  --integrity hmac-sha256  ...
+ cryptsetup --key-file key luksFormat --type luks2 --integrity hmac-sha256 /run/luks_integrity_benchmark/ramfs/image.raw
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 07:13.671, 80699 MiB written, speed 186,1 MiB/s
writing  ...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 78,852 s, 913 MB/s
 00:28:30 up  1:35,  3 users,  load average: 17,17, 8,62, 6,19
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 213,29 s, 338 MB/s
 00:32:36 up  1:39,  3 users,  load average: 3,53, 5,56, 5,47

               total        used        free      shared  buff/cache   available
Mem:           125Gi       5,1Gi        32Gi       149Mi        88Gi        35Gi

formatting with luks2   --cipher=chacha20-random  --integrity=poly1305  ...
+ cryptsetup --key-file key luksFormat --type luks2 --cipher=chacha20-random --integrity=poly1305 /run/luks_integrity_benchmark/ramfs/image.raw
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 04:08.553, 81296 MiB written, speed 327,1 MiB/s
writing  ...
+ dd if=/dev/zero bs=4096 count=17576663 of=/dev/mapper/luks_integrity_benchmark1
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 120,525 s, 597 MB/s
 00:39:26 up  1:46,  3 users,  load average: 21,99, 12,32, 7,81
reading it back:
+ dd if=/dev/mapper/luks_integrity_benchmark1 bs=4096 count=17576663 of=/dev/null
17576663+0 records in
17576663+0 records out
71994011648 bytes (72 GB, 67 GiB) copied, 120,92 s, 595 MB/s
 00:42:00 up  1:49,  3 users,  load average: 4,09, 8,43, 7,02

               total        used        free      shared  buff/cache   available
Mem:           125Gi       5,0Gi        32Gi       124Mi        88Gi        35Gi

```


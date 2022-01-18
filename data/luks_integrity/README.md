

```


root@r6 /d/h/d/luks_integrity (master) [1]# ./script1.sh
cleanup:
Device luks_integrity_benchmark1 is not active.

               total        used        free      shared  buff/cache   available
Mem:           125Gi       4,7Gi        73Gi       112Mi        47Gi        81Gi

raw write to ramfs:
39897624576 bytes (40 GB, 37 GiB) copied, 10 s, 4,0 GB/s
10000000+0 records in
10000000+0 records out
40960000000 bytes (41 GB, 38 GiB) copied, 10,2652 s, 4,0 GB/s
reading it back:
39905726464 bytes (40 GB, 37 GiB) copied, 5 s, 8,0 GB/s 
10000000+0 records in
10000000+0 records out
40960000000 bytes (41 GB, 38 GiB) copied, 5,13167 s, 8,0 GB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       4,7Gi        35Gi       107Mi        85Gi        43Gi

dm-integrity ...
Formatted with tag size 4, internal integrity crc32c.
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 00:08.503, 38696 MiB written, speed   4,4 GiB/s
32500051968 bytes (33 GB, 30 GiB) copied, 19 s, 1,7 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 25,9749 s, 1,3 GB/s
reading it back:
31402876928 bytes (31 GB, 29 GiB) copied, 14 s, 2,2 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 15,4915 s, 2,1 GB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       4,5Gi        35Gi       115Mi        85Gi        43Gi

formatting with luks2    ...
writing  ...
32673370112 bytes (33 GB, 30 GiB) copied, 16 s, 2,0 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 22,537 s, 1,5 GB/s
reading it back:
31205466112 bytes (31 GB, 29 GiB) copied, 16 s, 2,0 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 17,7361 s, 1,8 GB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       4,5Gi        35Gi       115Mi        85Gi        43Gi

formatting with luks2  --integrity hmac-sha1  ...
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 01:57.133, 37516 MiB written, speed 320,3 MiB/s
writing  ...
32528150528 bytes (33 GB, 30 GiB) copied, 26 s, 1,3 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 35,4599 s, 924 MB/s
reading it back:
32699170816 bytes (33 GB, 30 GiB) copied, 63 s, 519 MB/s 
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 64,0397 s, 512 MB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       4,9Gi        36Gi       128Mi        83Gi        43Gi

formatting with luks2  --integrity hmac-sha256  ...
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 03:15.557, 36688 MiB written, speed 187,6 MiB/s
writing  ...
31886843904 bytes (32 GB, 30 GiB) copied, 28 s, 1,1 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 37,9439 s, 864 MB/s
reading it back:
32483295232 bytes (32 GB, 30 GiB) copied, 97 s, 335 MB/s 
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 98,6971 s, 332 MB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       6,3Gi        35Gi       139Mi        83Gi        41Gi

formatting with luks2   --cipher=chacha20-random  --integrity=poly1305  ...
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 01:51.379, 36960 MiB written, speed 331,8 MiB/s
writing  ...
32269475840 bytes (32 GB, 30 GiB) copied, 42 s, 768 MB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 56,6848 s, 578 MB/s
reading it back:
32326402048 bytes (32 GB, 30 GiB) copied, 58 s, 557 MB/s 
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 59,7797 s, 548 MB/s

```


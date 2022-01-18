

```

root@r6 /d/h/d/luks_integrity (master) [5]# WORKDIR=/r3 ./script1.sh
cleanup:

               total        used        free      shared  buff/cache   available
Mem:           125Gi       7,1Gi        73Gi       224Mi        45Gi        79Gi

raw write to ramfs:
38763982848 bytes (39 GB, 36 GiB) copied, 10 s, 3,9 GB/s
10000000+0 records in
10000000+0 records out
40960000000 bytes (41 GB, 38 GiB) copied, 10,5581 s, 3,9 GB/s
reading it back:
37711093760 bytes (38 GB, 35 GiB) copied, 5 s, 7,5 GB/s 
10000000+0 records in
10000000+0 records out
40960000000 bytes (41 GB, 38 GiB) copied, 5,41643 s, 7,6 GB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       7,1Gi        34Gi       223Mi        83Gi        40Gi

dm-integrity ...
Formatted with tag size 4, internal integrity crc32c.
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 00:08.710, 38696 MiB written, speed   4,3 GiB/s
32426295296 bytes (32 GB, 30 GiB) copied, 20 s, 1,6 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 27,0424 s, 1,2 GB/s
reading it back:
30989467648 bytes (31 GB, 29 GiB) copied, 14 s, 2,2 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 15,698 s, 2,1 GB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       7,2Gi        34Gi       223Mi        83Gi        40Gi

formatting with luks2    ...
writing  ...
31875604480 bytes (32 GB, 30 GiB) copied, 16 s, 2,0 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 22,9288 s, 1,4 GB/s
reading it back:
31338250240 bytes (31 GB, 29 GiB) copied, 16 s, 2,0 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 17,6581 s, 1,9 GB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       7,2Gi        34Gi       237Mi        83Gi        40Gi

formatting with luks2  --integrity hmac-sha1  ...
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 01:56.584, 37516 MiB written, speed 321,8 MiB/s
writing  ...
32542384128 bytes (33 GB, 30 GiB) copied, 27 s, 1,2 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 35,843 s, 914 MB/s
reading it back:
32373587968 bytes (32 GB, 30 GiB) copied, 62 s, 522 MB/s 
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 63,6803 s, 515 MB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       7,3Gi        34Gi       232Mi        83Gi        40Gi

formatting with luks2  --integrity hmac-sha256  ...
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 03:16.889, 36688 MiB written, speed 186,3 MiB/s
writing  ...
32142893056 bytes (32 GB, 30 GiB) copied, 28 s, 1,1 GB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 37,6123 s, 871 MB/s
reading it back:
32676888576 bytes (33 GB, 30 GiB) copied, 98 s, 333 MB/s 
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 99,1985 s, 330 MB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       7,1Gi        35Gi       197Mi        83Gi        40Gi

formatting with luks2   --cipher=chacha20-random  --integrity=poly1305  ...
Wiping device to initialize integrity checksum.
You can interrupt this by pressing CTRL+c (rest of not wiped device will contain invalid checksum).
Finished, time 01:48.881, 36960 MiB written, speed 339,5 MiB/s
writing  ...
32631496704 bytes (33 GB, 30 GiB) copied, 43 s, 759 MB/s
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 56,6125 s, 579 MB/s
reading it back:
32664174592 bytes (33 GB, 30 GiB) copied, 58 s, 563 MB/s 
8000000+0 records in
8000000+0 records out
32768000000 bytes (33 GB, 31 GiB) copied, 59,0286 s, 555 MB/s

               total        used        free      shared  buff/cache   available
Mem:           125Gi       7,2Gi        35Gi       177Mi        83Gi        40Gi


```


#!/usr/bin/python3

import os
import sys
import shutil


def clean(path):
    """if disk space of /var/lib/motion is less than 20% then clean the oldest files from /var/lib/motion/archive"""

    disk = os.statvfs(path)
    free = disk.f_bavail * disk.f_frsize
    total = disk.f_blocks * disk.f_frsize
    used = (disk.f_blocks - disk.f_bfree) * disk.f_frsize
    percent = (used / total) * 100
    if percent > 80:
        print('Disk space is less than 20%')
        files = os.listdir(path)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)))
        for file in files[:1000]:
            os.remove(os.path.join(path, file))
        print(f'Cleaned {path}')
    else:
        print('Disk space is enough: ' + str(percent) + '%' + ' in ' + path)

if __name__ == '__main__':
    clean('/var/lib/motion/archive')
    clean('/var/lib/motion')

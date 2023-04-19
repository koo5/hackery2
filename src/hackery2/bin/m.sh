#!/usr/bin/env fish
mount | grep -v snap | grep -v noexec | grep -v nosuid | grep -v efi | grep -v binfmt_misc | grep -v hugepages

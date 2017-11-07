#!/usr/bin/env fish

git submodule update --init --force --recursive; git checkout 3rdparty/libshv ; git status

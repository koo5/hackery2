#!/usr/bin/env bash

dd bs=1048576 count=10240 if=/dev/zero of=/tmp/benchmark
dd bs=64 count=1 if=/dev/urandom of=/tmp/key


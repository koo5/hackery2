#!/usr/bin/env bash

fio --rw write --filename $BLOCK_DEVICE a.fio
fio --rw read --filename $BLOCK_DEVICE a.fio

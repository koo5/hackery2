#!/usr/bin/env bash

while true; do
ps -C swipl -o pid=,%mem=,vsz= >> /tmp/mem.log
gnuplot show_mem.plt
sleep 0.1
done 







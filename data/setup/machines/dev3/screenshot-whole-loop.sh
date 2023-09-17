#!/usr/bin/env bash

echo "start" >> /tmp/screenshot-whole-loop.log

screenshot-whole-loop.py /shared/screenshots/ 10 -u  | tee /tmp/screenshot-whole-loop.log


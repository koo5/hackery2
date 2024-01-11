#!/usr/bin/env fish

mkdir logs

reset; echo -e "\e[3J"; PYTHONUNBUFFERED=1 ./main.py 2>&1 | tee logs/(date -u '+%Y-%m-%d_%H-%M-%S')


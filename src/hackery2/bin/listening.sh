#!/usr/bin/env bash
ss -lnptu | awk 'NR>1 { split($7,p,","); split(p[2],pid,"="); printf "Listen: "$5 " Command: "; system("ps --no-headers -ww -o args p "pid[2]); }'
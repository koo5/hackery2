#!/usr/bin/env bash
#xrandr --output DP-2 --above DP-0
xrandr --setmonitor SomeName4 auto DP-1,DP-0
nohup xfwm4 --replace # disown?


#!/usr/bin/env bash
xrandr --output DP-0 --above DP-2
xrandr --setmonitor SomeName4 auto DP-0,DP-2
nohup xfwm4 --replace # disown?





#!/usr/bin/env bash
xrandr --output DP-5.2 --above DP-5.3
xrandr --setmonitor SomeName4 auto DP-5.2,DP-5.3
nohup xfwm4 --replace # disown?





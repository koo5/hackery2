#!/usr/bin/env bash
#randr --output DP-0 --above DisplayPort-1
#leep 1;
#randr --output DP-1 --above DisplayPort-2
#leep 1;

xrandr --setmonitor SomeName4 auto DisplayPort-0,DisplayPort-1,DisplayPort-2

#nohup xfwm4 --replace # disown?





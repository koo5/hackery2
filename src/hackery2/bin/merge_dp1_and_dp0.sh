#!/usr/bin/env bash
#xrandr --output DisplayPort-1 --above DisplayPort-0
xrandr --delmonitor SomeName4
xrandr --setmonitor SomeName4 auto DisplayPort-1,DisplayPort-0
cd ~
#nohup xfwm4 --replace # disown?
#nohup kwin --replace # disown?


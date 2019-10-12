#!/usr/bin/env bash
xrandr --newmode "2560x1440_50.00"  256.25  2560 2736 3008 3456  1440 1443 1448 1484 -hsync +vsync
xrandr --addmode Virtual-1 "2560x1440_50.00"
xrandr --output Virtual-1 --mode "2560x1440_50.00"



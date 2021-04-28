#!/usr/bin/env bash
#xrandr --newmode "2560x1440_50.00"  256.25  2560 2736 3008 3456  1440 1443 1448 1484 -hsync +vsync
#xrandr --newmode "1920x2080_50.00"  281.00  1920 2064 2272 2624  2080 2083 2093 2142 -hsync +vsync
#xrandr --addmode Virtual-1 1920x2080_50.00
#xrandr --output Virtual-1 --mode 1920x2080_50.00
xrandr --newmode "1600x900_50.00"   96.50  1600 1680 1840 2080  900 903 908 929 -hsync +vsync

xrandr --addmode Virtual-0 1600x900_50.00
xrandr --output Virtual-0 --mode 1600x900_50.00



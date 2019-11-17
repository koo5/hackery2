#!/usr/bin/env bash
#xrandr --newmode "2560x1440_50.00"  256.25  2560 2736 3008 3456  1440 1443 1448 1484 -hsync +vsync
#xrandr --newmode "1920x2080_50.00"  281.00  1920 2064 2272 2624  2080 2083 2093 2142 -hsync +vsync
#xrandr --addmode Virtual-1 1920x2080_50.00
#xrandr --output Virtual-1 --mode 1920x2080_50.00

xrandr --newmode "1920x2160_50.00"  293.50  1920 2072 2280 2640  2160 2163 2173 2225 -hsync +vsync
xrandr --addmode Virtual-0 1920x2160_50.00
xrandr --output Virtual-0 --mode 1920x2160_50.00
xrandr --addmode Virtual-1 1920x2160_50.00
xrandr --output Virtual-1 --mode 1920x2160_50.00


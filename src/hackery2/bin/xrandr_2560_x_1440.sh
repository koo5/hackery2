#!/usr/bin/env fish

set output $argv[1]
echo $output
xrandr --newmode "2560x1440_50.00"  256.25  2560 2736 3008 3456  1440 1443 1448 1484 -hsync +vsync
xrandr --addmode $output "2560x1440_50.00"  ;and \
xrandr --output $output --mode "2560x1440_50.00"  


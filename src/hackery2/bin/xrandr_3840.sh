#!/usr/bin/env fish

set output $argv[1]
echo $output
xrandr --newmode "3840x2160_60.00"  712.75  3840 4160 4576 5312  2160 2163 2168 2237 -hsync +vsync 
xrandr --addmode $output 3840x2160_60.00 ;and \
xrandr --output $output --mode 3840x2160_60.00 


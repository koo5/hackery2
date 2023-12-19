#!/usr/bin/env fish

#amixer -q -D pulse sset Capture toggle

pactl set-source-mute @DEFAULT_SOURCE@ toggle
notify-send (pactl get-source-mute @DEFAULT_SOURCE@)




#!/usr/bin/env fish
xset -dpms s off s noblank s 0 0 s noexpose
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.desktop.lockdown disable-lock-screen 'true'



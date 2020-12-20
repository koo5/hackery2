#!/usr/bin/env fish

fish -c xwininfo | grep 'Window id:' | sed 's/xwininfo: Window id: \(.*\) ".*/\1/'

#!/bin/bash

wid=$1
class=$2
instance=$3
consequences=$4
title=$(xtitle "$wid")
if [[ "$title" = "Desktop — Plasma" ]]; then
    xdotool windowclose "$wid"
fi


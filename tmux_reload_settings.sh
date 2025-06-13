#!/bin/bash

# This only works when run from within a tmux session and won't interfere with other sessions.

# Check if tmux is running
if ! pgrep -x "tmux" > /dev/null; then
    echo "tmux is not running"
    exit 1
fi

# Reload tmux configuration directly
if tmux source-file ~/.tmux.conf 2>/dev/null; then
    echo "Tmux configuration reloaded successfully"
else
    echo "Failed to reload tmux configuration"
    echo "Make sure you run this from within a tmux session"
    exit 1
fi
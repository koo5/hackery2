#!/usr/bin/env bash
# Install the numrow-remap udev rule, adapted to the local user and repo location.
# The rule re-applies the remap + key repeat rate whenever a keyboard (re)connects.
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO="$( git -C "$DIR" rev-parse --show-toplevel )"
RULE=/etc/udev/rules.d/95-remap-numrow.rules

# adapt the checked-in rule (written for koom@t14); order matters: longest match first
sed -e "s|/home/koom/hackery2|$REPO|g" \
    -e "s|/home/koom|$HOME|g" \
    -e "s|--uid=koom|--uid=$USER|g" \
    "$REPO/data/udev/95-remap-numrow.rules" | sudo tee "$RULE" >/dev/null

sudo udevadm control --reload
echo "installed $RULE (user=$USER repo=$REPO)"

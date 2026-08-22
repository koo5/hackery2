#!/usr/bin/env bash
# Install the Bluetooth power-management workaround for the Intel AX200 radio.
#
# Keeps the radio (8087:0029) out of USB runtime suspend, which on this machine
# can wedge it badly enough to kill the xHCI controller it lives on, taking
# Bluetooth and the fingerprint reader with it. See the header comments in the
# installed files for the full failure mode.
#
# Neither piece takes effect on an already-wedged radio - the radio needs a full
# poweroff. This makes the fix stick from the next boot onward.
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO="$( git -C "$DIR" rev-parse --show-toplevel )"

RULE=/etc/udev/rules.d/81-bluetooth-no-autosuspend.rules
MODCONF=/etc/modprobe.d/btusb-no-autosuspend.conf

sudo install -m 0644 "$REPO/data/udev/81-bluetooth-no-autosuspend.rules" "$RULE"
sudo install -m 0644 "$REPO/setup/data/modprobe.d/btusb-no-autosuspend.conf" "$MODCONF"

sudo udevadm control --reload

echo "installed $RULE"
echo "installed $MODCONF"
echo
echo "Takes effect on next btusb load. If the radio is currently wedged"
echo "(no /sys/class/bluetooth entries), a full poweroff is still required -"
echo "a warm reboot may not drop power to the M.2 slot."

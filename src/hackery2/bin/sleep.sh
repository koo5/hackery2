#!/usr/bin/env fish
set -x

sudo umount -f /home/koom/snap/firefox/common/.mozilla/firefox/hpp
sudo umount -f /home/koom/mnt/mnt3

set DISPLAY :0 
screen_off.sh
sudo rmmod -vvvv aquantia;
sudo rmmod -vvvv atlantic;
sleep 5;
all_usb_wakeup.sh disabled;

# amdgpu resume workaround: move X off the active VT before suspend so it drops
# DRM master. The console/fbcon owns the GPU across the deep-S3 cycle, and on
# resume X re-acquires master with a fresh modeset/context rebuild. This avoids
# the amdgpu_cs_submit NULL-deref where Xorg:cs0 submits against a stale context.
set orig_vt (sudo fgconsole 2>/dev/null)
test -z "$orig_vt"; and set orig_vt 1
sudo chvt 3

# drop a marker into the kernel log so we can slice exactly this resume's new lines,
# robust to the constant "[drm] scheduler ... not ready" spam wrapping the ring buffer
set marker claude-sleep-(date +%s)
echo $marker | sudo tee /dev/kmsg >/dev/null

sudo bash -c " echo mem > /sys/power/state" ;
sleep 10;
test -n "$orig_vt"; and sudo chvt $orig_vt
sudo modprobe -vvvv atlantic;

# persist this resume's kernel log slice for amdgpu crash triage (no journald changes)
set resume_log $HOME/.local/state/sleep-resume.log
mkdir -p (dirname $resume_log)
set dmesg_new (sudo dmesg | sed "0,/$marker/d")
begin
    echo "===== resume "(date -Iseconds)" (back to vt $orig_vt) ====="
    printf '%s\n' $dmesg_new
end >> $resume_log
if printf '%s\n' $dmesg_new | grep -q amdgpu_cs_submit
    echo "!!! amdgpu_cs_submit oops AFTER resume — full slice in $resume_log"
else
    echo "resume clean (no amdgpu_cs_submit) — logged to $resume_log"
end

sudo dmesg --follow;




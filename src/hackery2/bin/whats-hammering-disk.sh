#!/bin/bash
# whats-hammering-disk.sh — diagnose what's keeping a disk/mountpoint busy.
#
# Usage:
#   whats-hammering-disk.sh                  # auto-pick busiest device
#   whats-hammering-disk.sh /bac20           # mountpoint
#   whats-hammering-disk.sh /dev/mapper/foo  # device
#
# Looks for the classic "metadata walk" signature (100% util, tiny request
# size, low MB/s) versus bulk-IO patterns, and tries to attribute the load
# to a process — including find/du-style scans that don't show up cleanly
# in lsof because they hold no long-lived FDs.

set -u

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
fi

hdr() { printf '\n=== %s ===\n' "$*"; }

# --- Resolve target ----------------------------------------------------------

TARGET="${1:-}"
MOUNT=""
DEV=""

if [ -z "$TARGET" ]; then
    # Pick busiest device from a 2s iostat sample.
    DEV=$(iostat -xy 2 1 2>/dev/null \
        | awk '/^[a-z]/ && $NF+0 > 0 {print $NF, $1}' \
        | sort -nr | awk 'NR==1{print $2}')
    [ -n "$DEV" ] && DEV="/dev/$DEV"
elif [ -d "$TARGET" ]; then
    MOUNT="$TARGET"
    DEV=$(findmnt -no SOURCE "$MOUNT" 2>/dev/null)
elif [ -b "$TARGET" ]; then
    DEV="$TARGET"
    MOUNT=$(findmnt -no TARGET "$DEV" 2>/dev/null | head -1)
fi

if [ -z "$DEV" ]; then
    echo "Could not resolve target. Pass a mountpoint or block device." >&2
    exit 1
fi

# Map dm-N <-> /dev/mapper/* so iostat (which uses dm-N) matches the device.
DEV_BASENAME=$(basename "$DEV")
DM_NAME=""
if [ -L "$DEV" ]; then
    DM_NAME=$(basename "$(readlink -f "$DEV")")  # e.g. dm-3
fi
SYSFS_NAME="${DM_NAME:-$DEV_BASENAME}"

echo "Target: device=$DEV  mount=${MOUNT:-<none>}  iostat-name=$SYSFS_NAME"

# --- 1. IO pattern -----------------------------------------------------------

hdr "iostat (2x2s) — look at rareq-sz / wareq-sz and %util"
iostat -xy 2 2 "$DEV" 2>/dev/null \
    | awk -v d="$SYSFS_NAME" 'NR<=3 || $1==d || /^Device/ || /^avg-cpu/ || /^ /'

# Heuristic banner.
SAMPLE=$(iostat -xy 2 1 "$DEV" 2>/dev/null | awk -v d="$SYSFS_NAME" '$1==d {print; exit}')
if [ -n "$SAMPLE" ]; then
    RREQSZ=$(echo "$SAMPLE" | awk '{print $6+0}')
    WREQSZ=$(echo "$SAMPLE" | awk '{print $14+0}')
    UTIL=$(echo "$SAMPLE"   | awk '{print $NF+0}')
    RMB=$(echo "$SAMPLE"    | awk '{print $3/1024}')
    WMB=$(echo "$SAMPLE"    | awk '{print $11/1024}')
    echo
    awk -v u="$UTIL" -v r="$RREQSZ" -v w="$WREQSZ" -v rm="$RMB" -v wm="$WMB" 'BEGIN {
        printf "Signature: util=%.0f%%  read=%.1fMB/s (req=%.0fKB)  write=%.1fMB/s (req=%.0fKB)\n", u, rm, r, wm, w
        if (u > 80 && (r > 0 && r < 32) && rm < 20)
            print "-> Looks like METADATA WALK (small reqs, low throughput, pinned util)."
        else if (u > 80 && rm + wm > 50)
            print "-> Looks like BULK IO."
        else if (u > 80)
            print "-> Disk pinned but pattern unclear — check process list below."
    }'
fi

# --- 2. Process-level IO -----------------------------------------------------

hdr "iotop — top IO processes (2x1s, batch)"
$SUDO iotop -boP -n 2 -d 1 2>/dev/null | awk 'NR<=2 || $4 ~ /B\/s$/ && $4+0 > 0 || NR==3'

# --- 3. Filesystem-walk suspects ---------------------------------------------
# find/du/bfs/rsync/duperemove etc. often cause metadata-walk patterns and
# may not appear in lsof because they open files briefly.

hdr "Filesystem-walk suspects (find/bfs/du/rsync/dedup/borg/restic/...)"
ps -eo pid,user,stat,etime,cmd \
    | grep -iE '(^| )(find|bfs|fdfind|du|ncdu|rsync|duperemove|bedup|dedup|borg|restic|rclone|updatedb|mlocate|tracker-miner|baloo)( |$)' \
    | grep -v grep || echo "(none)"

# --- 4. Open files on the mount ---------------------------------------------

if [ -n "$MOUNT" ]; then
    hdr "lsof — processes holding files open on $MOUNT (top 20)"
    $SUDO lsof +D "$MOUNT" 2>/dev/null \
        | awk 'NR==1 || $4 ~ /[0-9]+[ruw]/' | head -20 || echo "(none)"
fi

# --- 5. Btrfs background ops -------------------------------------------------

FSTYPE=""
[ -n "$MOUNT" ] && FSTYPE=$(findmnt -no FSTYPE "$MOUNT" 2>/dev/null)
if [ "$FSTYPE" = "btrfs" ]; then
    hdr "btrfs background ops on $MOUNT"
    echo "-- balance --";    $SUDO btrfs balance status "$MOUNT" 2>&1 | head -5
    echo "-- scrub --";      $SUDO btrfs scrub  status "$MOUNT" 2>&1 | head -5
    echo "-- dev stats --";  $SUDO btrfs device stats  "$MOUNT" 2>&1 | head -10
    echo "-- qgroup --";     $SUDO btrfs qgroup show -prce "$MOUNT" 2>&1 | head -10
    echo "-- kernel threads --"
    ps -eo pid,stat,cmd | grep -E 'btrfs-(cleaner|transaction)|kworker/.*btrfs' | grep -v grep | head -20
fi

# --- 6. Hint ----------------------------------------------------------------

cat <<EOF

Tip: to confirm a suspect, pause it and re-check iostat:
    kill -STOP <pid> ; sleep 3 ; iostat -xy 2 1 $DEV ; kill -CONT <pid>
If %util drops while STOPped, you've found it.
EOF

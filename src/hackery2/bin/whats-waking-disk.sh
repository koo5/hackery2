#!/usr/bin/env bash
#
# whats-waking-disk.sh - find out what process physically wakes/touches a disk.
#
# ---------------------------------------------------------------------------
# Why this script exists (hard-won lessons):
#
#   * `fatrace <mount>` is the obvious tool and it is STRUCTURALLY BROKEN on
#     btrfs-with-subvolumes: "too many mounts" disables path resolution, and
#     -c/--current-mount ENOMEMs in open_by_handle_at across per-subvolume
#     fsids. It silently reports nothing useful.
#
#   * Path-level tracers (fatrace, opensnoop) get FOOLED BY CACHE. e.g.
#     `btrfs filesystem show` opens every btrfs mount but reads the superblock
#     from RAM, so they report "access" to a disk that never spun up.
#
#   * The GROUND TRUTH for a real spin-up is the BLOCK layer on the PHYSICAL
#     disk (tracepoint block:block_rq_issue). It cannot be faked by cache and
#     it also sees raw-device probes (SMART/udev/blkid) that bypass dm-crypt.
#     Watch the whole disk AND its partitions (filesystem I/O may be reported
#     against either dev_t).
#
#   * Common real culprit: udisksd SMART-polls every SATA drive every ~10 min
#     (an ATA passthrough; shows as comm=pool-udisksd, op "N", sectors=0).
#     That wakes an idle disk. USB-bridged drives that can't pass SMART are
#     not poked by udisks.
#
# Monitors are launched as transient systemd units so they outlive your shell
# and can be inspected with `journalctl -u <unit>` by you or anything else.
# ---------------------------------------------------------------------------
#
# Usage:
#   whats-waking-disk.sh resolve <mount|device>
#   whats-waking-disk.sh catch   <mount|device> [--exec] [--timeout SECS]
#   whats-waking-disk.sh watch   <mount|device> [--detail] [--bucket SECS] [--exec] [--opens]
#   whats-waking-disk.sh log     [<mount|device>] [block|exec|opens] [--since WHEN]
#   whats-waking-disk.sh status  [<mount|device>]
#   whats-waking-disk.sh stop    [<mount|device>]
#
# Examples:
#   sudo whats-waking-disk.sh catch /bac20 --exec        # block until first hit, name the culprit
#   sudo whats-waking-disk.sh watch /bac20               # durable low-footprint (5-min count buckets)
#   sudo whats-waking-disk.sh watch /bac20 --detail      # per-event detail (short investigations only)
#   sudo whats-waking-disk.sh log /bac20 --since '1 hour ago'
#   sudo whats-waking-disk.sh stop /bac20

set -euo pipefail

STATE_DIR="/run/whats-waking-disk"

die()       { echo "error: $*" >&2; exit 1; }
need_root() { [ "$(id -u)" -eq 0 ] || die "must run as root (use sudo)"; }
need_cmd()  { command -v "$1" >/dev/null 2>&1 || die "missing required tool: $1"; }

# kernel block-tracepoint dev_t encoding: (major << 20) | minor
devt() { echo $(( ($1 << 20) | $2 )); }

# Resolve a mountpoint or device to its physical disk and a bpftrace filter
# expression covering the whole disk plus all its partitions. Sets globals:
#   DISK_NAME, DISK_MAJMIN, DEV_FILTER, UNIT_BASE
resolve_disk() {
    local target="$1" src majmin
    [ -n "$target" ] || die "need a <mount|device>"

    if mountpoint -q "$target" 2>/dev/null; then
        src=$(findmnt -no SOURCE "$target") || die "cannot find source of mount $target"
    else
        src="$target"
    fi
    [ -b "$src" ] || src=$(readlink -f "$src" 2>/dev/null || echo "$src")
    [ -b "$src" ] || die "$src is not a block device (is the mount/crypt active?)"

    # Walk parents (inverse) to the whole disk; spin-up is a whole-disk property.
    # -r (raw) is essential: without it lsblk -s prepends tree-drawing chars to NAME.
    read -r DISK_NAME DISK_MAJMIN < <(
        lsblk -nrso NAME,MAJ:MIN,TYPE "$src" 2>/dev/null | awk '$3=="disk"{print $1, $2; exit}') || true
    [ -n "${DISK_NAME:-}" ] || die "could not resolve a physical disk behind $src"

    # Build OR-filter over the disk and its real partitions only (skip downstream
    # dm/crypt holders that lsblk lists in the same subtree - they're bio-based
    # and don't emit block_rq_issue anyway).
    local parts=() expr="" mm maj min
    while read -r mm; do
        [ -n "$mm" ] || continue
        maj=${mm%%:*}; min=${mm##*:}
        parts+=("$(devt "$maj" "$min")")
    done < <(lsblk -nro MAJ:MIN,TYPE "/dev/$DISK_NAME" 2>/dev/null \
                | awk '$2=="disk"||$2=="part"{print $1}')
    [ "${#parts[@]}" -gt 0 ] || die "could not enumerate dev_t for $DISK_NAME"
    for d in "${parts[@]}"; do
        expr="${expr:+$expr || }args->dev == $d"
    done
    DEV_FILTER="$expr"
    UNIT_BASE="wwd-${DISK_NAME}"
}

unit_block() { echo "${UNIT_BASE}-block"; }
unit_exec()  { echo "${UNIT_BASE}-exec"; }
unit_opens() { echo "${UNIT_BASE}-opens"; }

start_block_detail() {
    systemctl reset-failed "$(unit_block)" 2>/dev/null || true
    systemd-run --unit="$(unit_block)" --collect \
        bpftrace -e "tracepoint:block:block_rq_issue /${DEV_FILTER}/ {
            printf(\"%s %-16s pid=%-7d %-4s sectors=%d\\n\",
                   strftime(\"%H:%M:%S\", nsecs), comm, pid, args->rwbs, args->nr_sector); }" \
        >/dev/null
}

start_block_aggregate() {
    local bucket="$1"
    systemctl reset-failed "$(unit_block)" 2>/dev/null || true
    systemd-run --unit="$(unit_block)" --collect \
        bpftrace -e "tracepoint:block:block_rq_issue /${DEV_FILTER}/ { @[comm] = count(); }
            interval:s:${bucket} {
                printf(\"---- %s UTC ----\\n\", strftime(\"%H:%M:%S\", nsecs));
                print(@); clear(@); }" \
        >/dev/null
}

start_exec() {
    local pat="${1:-/(s?bin)/btrfs }"
    need_cmd execsnoop-bpfcc
    systemctl reset-failed "$(unit_exec)" 2>/dev/null || true
    systemd-run --unit="$(unit_exec)" --collect \
        bash -c "execsnoop-bpfcc 2>/dev/null | grep --line-buffered -E '${pat}'" >/dev/null
}

start_opens() {
    local path="$1"
    need_cmd opensnoop-bpfcc
    echo "  WARNING: opens monitor is system-wide BPF on every open() - CPU-heavy" >&2
    echo "           (~hours of CPU/day) and can cry wolf on cached metadata." >&2
    systemctl reset-failed "$(unit_opens)" 2>/dev/null || true
    systemd-run --unit="$(unit_opens)" --collect \
        bash -c "opensnoop-bpfcc 2>/dev/null | grep --line-buffered ' ${path}'" >/dev/null
}

# Strip systemd lifecycle noise and the bpftrace banner. The banner literally
# contains "pid=" (it's the command text), so real events are matched by their
# leading HH:MM:SS or the aggregate "----" separator.
clean_log() {
    grep -vE 'Started|Stopping|Stopped|Consumed|Deactiv|Attaching|Main PID|transient|invocation'
}

cmd_resolve() {
    resolve_disk "$1"
    echo "target       : $1"
    echo "physical disk: $DISK_NAME ($DISK_MAJMIN)"
    echo "model        : $(lsblk -ndo MODEL "/dev/$DISK_NAME" 2>/dev/null)"
    echo "dev filter   : $DEV_FILTER"
    echo "unit base    : $UNIT_BASE"
}

cmd_catch() {
    need_root; need_cmd bpftrace
    local target="${1:-}"; shift || true
    [ -n "$target" ] || die "usage: catch <mount|device> [--exec] [--timeout SECS]"
    local want_exec="" timeout=3600
    while [ $# -gt 0 ]; do
        case "$1" in
            --exec) want_exec=1 ;;
            --timeout) shift; timeout="$1" ;;
            --timeout=*) timeout="${1#--timeout=}" ;;
            *) die "unknown option: $1" ;;
        esac; shift
    done
    resolve_disk "$target"
    start_block_detail
    [ -n "$want_exec" ] && start_exec
    local b; b=$(unit_block)
    echo "watching $DISK_NAME ($DISK_MAJMIN) behind $target; armed $(date -u +%H:%M:%S) UTC"
    echo "waiting for first physical I/O (timeout ${timeout}s)..."

    local waited=0
    while [ "$waited" -lt "$timeout" ]; do
        if journalctl -u "$b" --no-pager -o cat --since "8s ago" 2>/dev/null \
             | grep -qE '^[0-9]{2}:[0-9]{2}:[0-9]{2} '; then
            echo "===== PHYSICAL I/O on $DISK_NAME at $(date -u +%H:%M:%S) UTC ====="
            echo "--- block events (last 60s) ---"
            journalctl -u "$b" --no-pager -o cat --since "60s ago" 2>/dev/null \
                | grep -E '^[0-9]{2}:[0-9]{2}:[0-9]{2} ' | head -40
            echo "--- comm/op breakdown ---"
            journalctl -u "$b" --no-pager -o cat --since "60s ago" 2>/dev/null \
                | grep -E '^[0-9]{2}:[0-9]{2}:[0-9]{2} ' | awk '{print $2, $4}' \
                | sort | uniq -c | sort -rn
            if [ -n "$want_exec" ]; then
                echo "--- short-lived commands (last 120s) ---"
                journalctl -u "$(unit_exec)" --no-pager -o cat --since "120s ago" 2>/dev/null \
                    | clean_log | head -20
            fi
            echo "(monitors left running; '$0 stop $target' to clean up)"
            return 0
        fi
        sleep 5; waited=$((waited + 5))
    done
    echo "no physical I/O in ${timeout}s (monitors still running)"
}

cmd_watch() {
    need_root; need_cmd bpftrace
    local target="${1:-}"; shift || true
    [ -n "$target" ] || die "usage: watch <mount|device> [--detail] [--bucket SECS] [--exec] [--opens]"
    local detail="" bucket=300 want_exec="" want_opens=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --detail) detail=1 ;;
            --bucket) shift; bucket="$1" ;;
            --bucket=*) bucket="${1#--bucket=}" ;;
            --exec) want_exec=1 ;;
            --opens) want_opens=1 ;;
            *) die "unknown option: $1" ;;
        esac; shift
    done
    resolve_disk "$target"
    mkdir -p "$STATE_DIR"
    printf '%s\t%s\t%s\n' "$target" "$DISK_NAME" "$DISK_MAJMIN" > "$STATE_DIR/$UNIT_BASE"

    if [ -n "$detail" ]; then
        start_block_detail
        echo "started $(unit_block) (per-event detail) on $DISK_NAME ($DISK_MAJMIN)"
    else
        start_block_aggregate "$bucket"
        echo "started $(unit_block) (${bucket}s count buckets) on $DISK_NAME ($DISK_MAJMIN)"
    fi
    [ -n "$want_exec" ]  && { start_exec;            echo "started $(unit_exec)"; }
    [ -n "$want_opens" ] && { start_opens "$target"; echo "started $(unit_opens)"; }
    echo "inspect: $0 log $target   |   stop: $0 stop $target"
}

# Map a target (or nothing) to a UNIT_BASE for log/status/stop.
base_for() {
    if [ -n "${1:-}" ]; then
        resolve_disk "$1"; echo "$UNIT_BASE"
    else
        # single watched disk? use it; else require an argument
        local found; found=$(ls "$STATE_DIR" 2>/dev/null) || true
        [ "$(echo "$found" | grep -c .)" = 1 ] || die "specify <mount|device> (multiple or none watched)"
        echo "$found"
    fi
}

cmd_log() {
    need_root
    local target="" which="block" since=""
    while [ $# -gt 0 ]; do
        case "$1" in
            block|exec|opens) which="$1" ;;
            --since) shift; since="$1" ;;
            --since=*) since="${1#--since=}" ;;
            *) target="$1" ;;
        esac; shift
    done
    local base; base=$(base_for "$target")
    local args=(-u "${base}-${which}" --no-pager -o cat)
    [ -n "$since" ] && args+=(--since "$since")
    journalctl "${args[@]}" 2>/dev/null | clean_log || true
}

cmd_status() {
    need_root
    local target="${1:-}"
    local bases
    if [ -n "$target" ]; then bases=$(base_for "$target"); else bases=$(ls "$STATE_DIR" 2>/dev/null || true); fi
    [ -n "$bases" ] || { echo "no monitors running"; return 0; }
    for base in $bases; do
        [ -f "$STATE_DIR/$base" ] && echo "== $base ($(cut -f1 "$STATE_DIR/$base") -> $(cut -f2,3 "$STATE_DIR/$base" | tr '\t' ' ')) =="
        for role in block exec opens; do
            printf '   %-22s ' "${base}-${role}"
            systemctl is-active "${base}-${role}" 2>/dev/null || true
        done
    done
}

cmd_stop() {
    need_root
    local target="${1:-}"
    local bases
    if [ -n "$target" ]; then bases=$(base_for "$target"); else bases=$(ls "$STATE_DIR" 2>/dev/null || true); fi
    [ -n "$bases" ] || { echo "nothing to stop"; return 0; }
    for base in $bases; do
        for role in block exec opens; do
            systemctl stop "${base}-${role}" 2>/dev/null || true
            systemctl reset-failed "${base}-${role}" 2>/dev/null || true
        done
        rm -f "$STATE_DIR/$base"
        echo "stopped $base monitors"
    done
}

case "${1:-}" in
    resolve) shift; cmd_resolve "$@" ;;
    catch)   shift; cmd_catch   "$@" ;;
    watch)   shift; cmd_watch   "$@" ;;
    log)     shift; cmd_log     "$@" ;;
    status)  shift; cmd_status  "$@" ;;
    stop)    shift; cmd_stop    "$@" ;;
    ""|-h|--help) sed -n '/^# Usage:/,/^#   sudo whats-waking-disk.sh stop/p' "$0" | sed 's/^# \{0,1\}//' ;;
    *) die "unknown command: $1 (try --help)" ;;
esac

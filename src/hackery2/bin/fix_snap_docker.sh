#!/usr/bin/env bash
# Recover Docker after GParted leaves runtime masks on /snap and /var.
# Usage: fix_snap_docker.sh (requests sudo when needed)
set -euo pipefail

if pgrep -x gparted >/dev/null || pgrep -x gpartedbin >/dev/null; then
    echo 'Close GParted before running this script; its mount masks protect partition operations.' >&2
    exit 1
fi

if (( EUID != 0 )); then
    exec sudo -- bash "$(readlink -f -- "$0")" "$@"
fi

# Only remove the runtime masks involved in this failure, preserving permanent masks.
systemctl unmask --runtime snap.mount var.mount
snap start docker.dockerd

# snap start can return before the Docker API is ready.
for ((attempt = 0; attempt < 30; attempt++)); do
    if timeout 2 docker --host unix:///var/run/docker.sock info \
        --format 'Docker {{.ServerVersion}} is ready; {{.ContainersRunning}} container(s) running.' \
        2>/dev/null; then
        exit 0
    fi
    sleep 1
done

echo 'Docker did not become ready. Recent service logs:' >&2
journalctl -u snap.docker.dockerd.service -n 40 --no-pager >&2
exit 1

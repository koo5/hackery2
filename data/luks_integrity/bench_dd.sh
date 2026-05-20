#!/usr/bin/env bash
# Wrapper around dd that captures and logs the transfer speed.
# Usage: bench_dd.sh "label" dd [dd args...]
LABEL="$1"
shift

TMPFILE=$(mktemp)
"$@" 2>&1 | tee "$TMPFILE"
SPEED=$(grep -oP '[\d.,]+ [KMGT]?B/s' "$TMPFILE" | tail -1)
echo "$LABEL|$SPEED" >> "$RESULTS_FILE"
rm -f "$TMPFILE"

#!/bin/bash

# Array to hold PIDs
pids=()

# Function to kill all tail processes
cleanup() {
  echo "Stopping all tail processes..."
  for pid in "${pids[@]}"; do
    kill "$pid"
  done
}

# Set trap to call cleanup on SIGINT (Ctrl+C)
trap cleanup SIGINT

# Loop over files and tail each in background
for file in $@; do
  if [ -f "$file" ]; then
    tail -f "$file" | awk -v fname="$file" '{print fname ": " $0}' &
    pids+=("$!")
  fi
done

# Wait for all tail processes to finish (optional, depends on your use case)
wait

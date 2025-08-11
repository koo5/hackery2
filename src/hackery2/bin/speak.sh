#!/usr/bin/env bash
~/vvvv/venv/bin/piper  --model ~/vvvv/en_US-lessac-medium.onnx --output-raw --length-scale 1.5 |   aplay -r 22050 -f S16_LE -t raw -



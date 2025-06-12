#!/bin/bash
# Setup multiple audio outputs with PipeWire/PulseAudio

# List available sinks
echo "Available audio sinks:"
pactl list short sinks

# Create a combined sink with your specific devices
# Replace sink1 and sink2 with actual sink names from the list above
pactl load-module module-combine-sink \
    sink_name=combined \
    slaves=sink1,sink2 \
    sink_properties="device.description='Combined Output'"

# Set the combined sink as default
pactl set-default-sink combined

echo "Combined sink created. Use 'pavucontrol' to manage per-application routing."
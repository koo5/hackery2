#!/usr/bin/env bash

# $@:   List of sinks to combine, as `CARD_ID:DEVICE_ID`
__os_audio_sinks_combine() {
  unset sink_names
  for i; do
    curr_sink_id="${i%%:*}"
    curr_device_id="${i#*:}"
    
    curr_device_name="hw:${curr_sink_id},${curr_device_id}"
    
    curr_sink_name="vsink_${curr_sink_id}${curr_device_id}"
    
    test -n "${sink_names}" && sink_names="${sink_names},"
    sink_names="${sink_names}${curr_sink_name}"
    
    curr_device_desc="HDMI ${curr_device_id} VSINK"
    
    echo "load-module module-alsa-sink device=\"${curr_device_name}\" sink_name=${curr_sink_name} sink_properties=\"device.description='${curr_device_id}' device.icon_name='audio-card'\""
  done

  echo "load-module module-combine-sink sink_name=combined_vsink slaves=${sink_names} sink_properties=\"device.description='comb_vsink' device.icon_name='audio-card-symbolic'\""
}

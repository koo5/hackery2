#!/usr/bin/env bash

sudo mmcli -m 5 \
             --location-enable-gps-raw \
             --location-enable-gps-nmea

mmcli -m 5 --location-status

gpscat /dev/ttyUSB2
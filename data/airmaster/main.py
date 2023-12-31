#!/usr/bin/env python3

import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

token = os.environ.get("INFLUXDB_TOKEN")
org = "sfi"
url = "http://localhost:10101"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)

bucket="iot"

write_api = client.write_api(write_options=SYNCHRONOUS)
   
for value in range(5):
  point = (
    Point("measurement1")
    .tag("tagname1", "tagvalue1")
    .field("field1", value)
  )
  write_api.write(bucket=bucket, org="sfi", record=point)
  print('sleep..')
  time.sleep(1) # separate points by 1 second

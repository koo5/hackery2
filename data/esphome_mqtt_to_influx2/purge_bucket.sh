#!/usr/bin/env fish

influx delete --bucket $INFLUXDB_V2_BUCKET --start '2009-01-02T23:00:00Z' --stop '2029-01-02T23:00:00Z'

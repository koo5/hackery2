







def mqtt_log_line_to_influx(line):
	parse_mqtt_log_line(line)

def parse_mqtt_log_line(line):




def test():

	assert [mqtt_log_line_to_influx(line) for line in """
	homeassistant/button/zima/start_hp/config {"name":"Start hp","cmd_t":"zima/button/start_hp/command","avty_t":"zima/status","uniq_id":"ESPbuttonstart_hp","dev":{"ids":"a020a61c3105","name":"zima","sw":"esphome v2024.1.0-dev Jan  3 2024, 20:56:34","mdl":"nodemcu","mf":"espressif","sa":""}}
	fazole/debug [V][mqtt:474]: Publish(topic='fazole/climate/pump1_t/target_temperature/state' payload='14.0' retain=1)
	fazole/sensor/next_sunrise/state 08:01:02
	fazole/sensor/next_sunset/state 16:12:08
	fazole/sensor/time_ntp/state 2024-01-02 23:52:18
	fazole/sensor/uptime_sensor/state 465
	fazole/sensor/sun_elevation/state -62.7
	fazole/sensor/sun_azimuth/state 352.9
	fazole/sensor/wetness_raw1/state -1.29
	fazole/sensor/wetness1/state 21.77
	fazole/sensor/wetness_raw2/state 2.07
	fazole/sensor/wetness2/state 1.94
	fazole/sensor/wetness_raw3/state 28.58
	fazole/sensor/wetness3/state 15.99
	fazole/sensor/wetness_raw4/state 1.99
	fazole/sensor/wetness4/state 1.97
	fazole/sensor/irrigation_wifi/state -19
	fazole/switch/living_room_restart/state OFF
	fazole/switch/pump1/state OFF
	fazole/switch/pump2/state OFF
	fazole/switch/pump3/state OFF
	fazole/switch/pump4/state OFF
	fazole/climate/pump1_t/mode/state heat
	fazole/climate/pump1_t/current_temperature/state 7.7
	fazole/climate/pump1_t/target_temperature/state 14.0
	fazole/climate/pump1_t/preset/state home
	fazole/climate/pump1_t/action/state off
	fazole/climate/pump2_t/mode/state heat
	fazole/climate/pump2_t/current_temperature/state 1.9
	fazole/climate/pump2_t/target_temperature/state 14.0
	fazole/climate/pump2_t/preset/state home
	fazole/climate/pump2_t/action/state off
	fazole/climate/pump3_t/mode/state heat
	fazole/climate/pump3_t/current_temperature/state 16.0
	fazole/climate/pump3_t/target_temperature/state 14.0
	fazole/climate/pump3_t/preset/state home
	fazole/climate/pump3_t/action/state off
	fazole/climate/pump4_t/mode/state heat
	fazole/climate/pump4_t/current_temperature/state 2.0
	fazole/climate/pump4_t/target_temperature/state 14.0
	fazole/climate/pump4_t/preset/state home
	fazole/climate/pump4_t/action/state off
	fazole/number/last_pump_ts_1/state 1704234880.000000
	fazole/number/last_pump_ts_2/state 1704234880.000000
	fazole/number/last_pump_ts_3/state 1704234880.000000
	fazole/number/last_pump_ts_4/state 1704234880.000000
	fazole/status offline
	esphome/discover/zima {"ip":"192.168.8.30","name":"zima","port":6053,"version":"2024.1.0-dev","mac":"a020a61c3105","platform":"ESP8266","board":"nodemcu","network":"wifi"}
	"""] == [



		]



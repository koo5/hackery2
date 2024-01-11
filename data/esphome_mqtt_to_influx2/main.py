#!/usr/bin/env python3

"""

connect to mqtt broker and subscribe to all topics. Connect to influxdb 2v, and submit each message as a measurement.

"""
import datetime
import json
import os
import queue
import subprocess
import time




from secrets import secret

influxdb_config = dict(
	url = 			secret('INFLUXDB_V2_URL', 				'http://localhost:8086'),
	token = 		secret('INFLUXDB_V2_WRITE_TOKEN', 		'Af5Z...wM=='),
	org = 			secret('INFLUXDB_V2_ORG', 				'sfi'),
	bucket = 		secret('INFLUXDB_V2_BUCKET', 			'iot2'),
)


mqtt_config = dict(
	host = 			secret('MQTT_HOST', 					'localhost'),
	port = 		int(secret('MQTT_PORT', 					'1883')),
	user = 			secret('MQTT_USER', 					'user'),
	password =		secret('MQTT_PASS', 					'password'),
	keepalive =	int(secret('MQTT_KEEPALIVE_INTERVAL_SECS',	60)),
)



hostname = subprocess.check_output(['hostname'], text=True).strip()



import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, 


if os.environ.get('DEBUG_AUTH'):
	print(f"""connecting to influxdb url={influxdb_config}""")
else:
	print(f"""connecting to influxdb url={influxdb_config['url']}, token={influxdb_config['token'][:1]}..{influxdb_config['token'][-1:]}, {influxdb_config['org']=}, {influxdb_config['bucket']=}""")


influx_client = InfluxDBClient(
	url=influxdb_config['url'],
	token=influxdb_config['token'],
	org=influxdb_config['org'],
	
	enable_gzip=True,
	
)

#with influx_client:
print(f"""influxdb version: {influx_client.health().version}""")

write_api = influx_client.write_api(write_options=SYNCHRONOUS)


import threading

uptime = 0
process_started = datetime.datetime.utcnow().isoformat()


def uptime_loop():
	global uptime
	sleep_secs = 1#60
	while True:
		time.sleep(sleep_secs)
		uptime += sleep_secs
		write_uptime()



outflux = queue.Queue()


def write_uptime():
	for point in uptime_points():
		outflux.push(point)

threading.Thread(target=uptime_loop, name='esphome_mqtt_to_influx2_uptime').start()





def outflux_loop():
	while True:
		write_api.write(bucket=influxdb_config['bucket'], org=influxdb_config['org'], record=outflux.get())



threading.Thread(target=outflux_loop, name='outflux').start()





def uptime_points():
	return [
		Point('server').
				tag("host", hostname).
				tag("service", 'esphome_mqtt_to_influx2').
				tag("process_started", str(process_started)).
				field("uptime", uptime),
		Point('server').
				tag("host", hostname).
				field("unix_timestamp", time.time())
	]



def write_uptime_sync():
	write_api.write(
		bucket=influxdb_config['bucket'], 
		org=influxdb_config['org'],
		record=uptime_points()[0])
		 
	
write_uptime_sync()





# MQTT callbacks

def on_connect(client, userdata, flags, rc, properties=None):
	print(f""""Connected to MQTT server: {userdata['host']}, {flags=}, {rc=}, {properties=}""")
	client.subscribe("#", qos=2)



def on_message(client, userdata, msg):

	topic = msg.topic
	payload = msg.payload.decode()
	
	print(f"{topic} : {payload.__repr__()}")
	point = esphome_to_influx(topic, payload)
	
	outflux.put(point)
	print(f"outflux queue length: {outflux.qsize()}")



def esphome_to_influx(topic, payload):
	
	topic = topic.split('/')
		
	def t(idx):
		try:
			return topic[idx]
		except IndexError:
			return None
	
	if topic[-1] not in ['debug', 'state']:
		return
	
	if topic[-1] == 'state':
		topic = topic[:-1]
		
	try:
		payload = float(payload)
	except ValueError:
		pass
			
	host = t(0)
	category = t(1)
	component = None
	property = t(2) if len(topic) > 2 else t(1)
	
	if len(topic) > 3:
		component = t(2)
		property = t(3)
	
	point = Point(category).field(property, payload)
	
	if host:
		point = point.tag("host", host)
	
	if component:
		point = point.tag("component", component)

	return point




if os.environ.get('DEBUG_AUTH'):
	print(f"""Connecting to mqtt broker {mqtt_config=}""")
else:
	print(f"""Connecting to mqtt broker host={mqtt_config['host']}""")



mqtt_client = mqtt.Client(
	client_id='esphome_mqtt_to_influx2__on__'+hostname+'__'+str(os.getpid()), 
	userdata=mqtt_config,
	protocol=mqtt.MQTTv5)
#mqtt_client.enable_logger()
mqtt_client.username_pw_set(mqtt_config['user'], mqtt_config['password'])
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

@mqtt_client.log_callback()
def on_log(client, userdata, level, buf):
	print(f"MQTT log: {level=}, {buf=}")
#
mqtt_client.connect(
	host=mqtt_config['host'], 
	port=mqtt_config['port'], 
	keepalive=mqtt_config['keepalive']
)




#
mqtt_client.loop_forever()


#!/usr/bin/env python3

"""

connect to mqtt broker and subscribe to all topics. Connect to influxdb 2v, and submit each message as a measurement.

"""
import sys
import threading
import datetime
import os
import queue
import subprocess
import time
import logging



logging.basicConfig(level=logging.DEBUG)
debug = logging.getLogger(__name__).debug



process_started = datetime.datetime.utcnow()
hostname = subprocess.check_output(['hostname'], text=True).strip()



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







import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, WriteApi 


if os.environ.get('DEBUG_AUTH'):
	debug(f"""connecting to influxdb url={influxdb_config}""")
else:
	debug(f"""connecting to influxdb url={influxdb_config['url']}, token={influxdb_config['token'][:1]}..{influxdb_config['token'][-1:]}, {influxdb_config['org']=}, {influxdb_config['bucket']=}""")


def uptime():
	return float((datetime.datetime.utcnow() - process_started).total_seconds())

def uptime_points(note):
	return [
		Point('server').
				tag("host", hostname).
				tag('note', note).
				tag("service", 'esphome_mqtt_to_influx2').
				tag("process_started", str(process_started.isoformat())).
				field("uptime", uptime()),
		Point('server').
				tag("host", hostname).
				tag('note', note).
				tag("service", 'esphome_mqtt_to_influx2').
				tag("process_started", str(process_started.isoformat())).
				field("unix_timestamp", time.time()),
		Point('server').
				tag("host", hostname).
				tag('note', note).
				tag("service", 'esphome_mqtt_to_influx2').
				tag("process_started", str(process_started.isoformat())).
				field("datetime", datetime.datetime.utcnow().isoformat())
	]


	

def make_influx_client():
	return InfluxDBClient(
		url=influxdb_config['url'],
		token=influxdb_config['token'],
		org=influxdb_config['org'],
	
		enable_gzip=True,
	)



with make_influx_client() as synchronous_influx_client:
	debug(f"""influxdb version: {synchronous_influx_client.health()}""")
	with synchronous_influx_client.write_api(write_options=SYNCHRONOUS) as write_api:
		write_api.write(
			bucket=influxdb_config['bucket'], 
			org=influxdb_config['org'],
			record=uptime_points('start')[0]
		)
	



outflux = queue.Queue()


def outflux_loop():
	try:		
		with make_influx_client() as influx_client:
			write_api = WriteApi(influxdb_client=influx_client)
			while True:
				point = outflux.get()
				write_api.write(bucket=influxdb_config['bucket'], org=influxdb_config['org'], record=point)
	except Exception as e:
		debug(f"outflux_loop: {e}")
		sys.exit(1)

threading.Thread(target=outflux_loop, name='outflux', daemon=True).start()






def uptime_loop():
	try:
		sleep_secs = 1
		while True:
			time.sleep(sleep_secs)
			for point in uptime_points('outflux_thread_writer_batched'):
				outflux.put(point)
	except Exception as e:
		debug(f"loop: {e}")
		sys.exit(1)


def uptime_loop2():
	try:
		with make_influx_client() as influx_client:
			write_api2 = WriteApi(influxdb_client=influx_client, write_options=SYNCHRONOUS)
			sleep_secs = 1
			while True:
				time.sleep(sleep_secs)
				for point in uptime_points('synchronous_writer'):
					write_api2.write(bucket=influxdb_config['bucket'], org=influxdb_config['org'], record=point)
	except Exception as e:
		debug(f"loop: {e}")
		sys.exit(1)
	


threading.Thread(target=uptime_loop, name='esphome_mqtt_to_influx2_uptime', daemon=True).start()
threading.Thread(target=uptime_loop2, name='esphome_mqtt_to_influx2_uptime2', daemon=True).start()






# MQTT callbacks

def on_connect(client, userdata, flags, rc, properties=None):
	debug(f""""Connected to MQTT server: {userdata['host']}, {flags=}, {rc=}, {properties=}""")
	client.subscribe("#", qos=2)



def on_message(client, userdata, msg):

	ts = datetime.datetime.utcnow()
	topic = msg.topic
	payload = msg.payload.decode()
	
	debug(f"on_message: {topic} : {payload.__repr__()}")
	
	point = esphome_to_influx(topic, payload)
	if point is None:
		return
		
	point.time(ts)
	
	debug(f'point={str(point)}')
	
	outflux.put(point)

	qs = outflux.qsize()
	if qs > 100:
		debug(f"outflux queue length: {qs}")
	


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
		
	topic = list(map(fix_field, topic))
		
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



def fix_field(field):
	if field.startswith('_'):
		field = 'X' + field[1:]
	return field


if os.environ.get('DEBUG_AUTH'):
	debug(f"""Connecting to mqtt broker {mqtt_config=}""")
else:
	debug(f"""Connecting to mqtt broker host={mqtt_config['host']}""")



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
	#debug(f"MQTT log: {level=}, {buf=}")
	pass
#
mqtt_client.connect(
	host=mqtt_config['host'], 
	port=mqtt_config['port'], 
	keepalive=mqtt_config['keepalive']
)



#
mqtt_client.loop_forever()


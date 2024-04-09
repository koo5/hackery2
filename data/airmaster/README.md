# AirMaster AM7, linux c++ serial port reader and mosquitto relay 

based on https://github.com/SergiySeletsky/air-master-esphome/

### deps
```
sudo apt-get install libmosquitto-dev
```
### build
```
g++ -Wall -o your_program_name test.cpp -lmosquitto
```
or:
```
 clang++ -I/usr/include/c++/11 -I/usr/include/x86_64-linux-gnu/c++/11 -L /usr/lib/gcc/x86_64-linux-gnu/11  -Wall -o your_program_name test.cpp -lmosquitto
```
### run
```
./your_program_name
```
or
```
sudo AM7_PORT=/dev/ttyUSB1 MQTT_PORT=1883 MQTT_HOST=public.mqtthq.com valgrind ./your_program_name
```
### output
```
AM7_PORT not set, using /dev/ttyUSB0
Serial communication initialized.
MQTT_HOST environment variable not set
Can't publish to topic am7/sensor/hello/state
40 Data received.

PM2.5: 1 ug/m3
PM10: 1 ug/m3
HCHO: 0.12 ug/m3
TVOC: 0.62 ug/m3
CO2: 1049 ppm
Temp: 25.9 °C
Hum: 52.7 %
PM0.3: 329 ppm
PM0.5: 46 ppm
PM1.0: 8 ppm
PM2.5: 0 ppm
PM5.0: 0 ppm
PM10: 0 ppm

40 Data received.

PM2.5: 1 ug/m3
...
```

## see also

https://github.com/reejk/AirMasterConnect/
#!/usr/bin/env python3
"""
Upper-case echo on /dev/ttyUSB0 @ 9600 8N1
Connect a remote device to this port and whatever it sends will come back in caps.
"""

import signal
import sys
import serial   # pip install pyserial

PORT = "/dev/ttyUSB0"
BAUD = 9600
TIMEOUT = 1.0          # seconds

def main():
	ser = serial.Serial(
		port=PORT,
		baudrate=BAUD,
		bytesize=serial.EIGHTBITS,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		timeout=TIMEOUT,
		write_timeout=TIMEOUT,
	)

	# Close port cleanly on Ctrl-C
	signal.signal(signal.SIGINT, lambda *_: (ser.close(), sys.exit(0)))

	print(f"ECHO → uppercase on {PORT} @ {BAUD} bps (Ctrl-C to quit)")

	while True:
		# Read all available bytes (or block for 1 byte)
		data = ser.read(ser.in_waiting or 1)
		if data:
			#sys.stdout.write(data.decode('utf-8'))
			print(data)
			#print(data.decode('utf-8'), end='', flush=True)
			ser.write(data.upper())
			ser.flush()          # ensure it actually leaves the OS buffer

if __name__ == "__main__":
	main()

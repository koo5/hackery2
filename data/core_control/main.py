#!/usr/bin/env python3

import re, os, time, shlex, re
import socket, logging
import subprocess, pathlib


logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def set_cores(num):
	print("Setting cores to: ", num)


svr = socket.socket(socket.AF_INET)
svr.bind(("0.0.0.0",1111))
svr.listen()



pattern = re.compile(r'GET /set_cores=(\d+) HTTP/1.1')


# Accepting client connections
while(True):
	log.info("srv.accept:")
	clientSocket, clientAddress = svr.accept()
	fileObject = clientSocket.makefile("rb", buffering=0)
	try:

		for line in fileObject:
			line = line.decode("utf-8").strip()
			#print(line)

			match = pattern.match(line)
			if match:
				num_cores = int(match.group(1))
				set_cores(num_cores)


	finally:
		fileObject.close()
		clientSocket.close()

	time.sleep(1)


#!/usr/bin/env python3

import re, os, time, shlex
import socket, logging
import subprocess, pathlib




logging.basicConfig(level=logging.DEBUG)



log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.info("info from main.py")
log.debug("debug from main.py")
log.warning("warning from main.py")



def check_ip(ip):
	# match valid ipv4 or ipv6 address
	if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', remote_ip):
		print("Valid IP address")
		return True
	if re.match(r'^[0-9a-fA-F:]+$', remote_ip):
		print("Valid IPv6 address")
		return True
	log.warning("Invalid IP address")
	return False




time.sleep(5)


# Create server socket
svr = socket.socket(socket.AF_INET)

# Bind to an IP & port
svr.bind(("127.0.0.1",11112))

log.info('Enter into listening state')
svr.listen()


stuff = 'X-Forwarded-For: '


# Accepting client connections
while(True):
	log.info("srv.accept:")

	clientSocket, clientAddress = svr.accept()

	fileObject = clientSocket.makefile("rb", buffering=0)
	
	for line in fileObject:
		line = line.decode("utf-8").strip()
		log.debug(line)
		if line.startswith(stuff):
			remote_ip = line[len(stuff):]
			if not check_ip(remote_ip):
				break

			for port in [44, 2222, 9192]:
				cmd = ['sudo', 'ufw', 'allow', 'from', remote_ip, 'to', 'any', 'port', str(port)]
				log.info(shlex.join(cmd))
				subprocess.run(cmd)
			break

	fileObject.close()
	clientSocket.close()

	time.sleep(15)
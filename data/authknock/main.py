#!/usr/bin/env python3

import re, os, time, shlex
import socket
import subprocess, pathlib



def check_ip(ip):
	# match valid ipv4 or ipv6 address
	if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', remote_ip):
		print("Valid IP address")
		return True
	if re.match(r'^[0-9a-fA-F:]+$', remote_ip):
		print("Valid IPv6 address")
		return True
	print("Invalid IP address")
	return False




# Create server socket
svr = socket.socket(socket.AF_INET)

# Bind to an IP & port
svr.bind(("127.0.0.1",11112))

# Enter into listening state
svr.listen()


stuff = 'X-Forwarded-For: '


# Accepting client connections
while(True):
	print("Listening for incoming connections:")

	clientSocket, clientAddress = svr.accept()

	

	fileObject = clientSocket.makefile("rb", buffering=0)
	
	for line in fileObject:
		line = line.decode("utf-8").strip()
		print(line)
		if line.startswith(stuff):
			remote_ip = line[len(stuff):]
			if not check_ip(remote_ip):
				break

			for port in [44, 2222, 9192]:
				cmd = ['sudo', 'ufw', 'allow', 'from', remote_ip, 'to', 'any', 'port', str(port)]
				print(shlex.join(cmd))
				subprocess.run(cmd)
			break

	fileObject.close()
	clientSocket.close()

	time.sleep(5)
import re, os
import socket
import subprocess, pathlib

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
			# match valid ipv4 or ipv6 address
			if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', remote_ip):
				print("Valid IP address")
			if re.match(r'^[0-9a-fA-F:]+$', remote_ip):
				print("Valid IPv6 address")

			subprocess.run([os.expanduser('~/magic_gate.py'), remote_ip])


	fileObject.close()
	clientSocket.close()

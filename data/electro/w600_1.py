https://bigl.es/microcontroller-monday-wemos-w600-pico/
https://drive.google.com/file/d/1qCvD3ZlEkNoJyoEa_Hlw1Ei1yq9ZsJbG/view

ctrl-e




#import sys
#sys.stdout.write("""

import utime
import network

def reconnect():
	sta_if = network.WLAN(network.STA_IF)
	while not sta_if.isconnected():
		print('connecting..')
		sta_if.active(True)
		sta_if.scan()
		sta_if.connect("---","---")
		x = 0
		while not sta_if.isconnected():
			utime.sleep_ms(100)
			x += 1
			if x > 10:
				print('.')
				x = 0
		sta_if.ifconfig(('10.0.0.75', '255.255.255.0', '10.0.0.138', '8.8.8.8'))
		print(sta_if.ifconfig())
		
reconnect()
import easyw600
easyw600.ftpserver()

print('sleep..')
utime.sleep_ms(1000)
print('sleep..')
utime.sleep_ms(1000)
print('sleep..')
utime.sleep_ms(1000)

# now use usocket as usual
import usocket as socket
addr = socket.getaddrinfo('micropython.org', 80)[0][-1]
s = socket.socket()
print(addr)
s.connect(addr)
s.send(b'GET / HTTP/1.1\\r\\nHost: micropython.org\\r\\n\\r\\n')
print(s)
data = s.recv(1000)
print(data)
s.close()
print()
print()

#""".replace('\t','\\t').replace('\n','\\n').replace('\\','\\\\'))



'import utime\nimport network\n\ndef reconnect():\n\tsta_if = network.WLAN(network.STA_IF)\n\twhile not sta_if.isconnected():\n\t\tprint(\'connecting..\')\n\t\tsta_if.active(True)\n\t\tsta_if.scan()\n\t\tsta_if.connect("ADSLvole","[][][][][][][][][][]")\n\t\tx = 0\n\t\twhile not sta_if.isconnected():\n\t\t\tutime.sleep_ms(100)\n\t\t\tx += 1\n\t\t\tif x > 10:\n\t\t\t\tprint(\'.\')\n\t\t\t\tx = 0\n\t\tsta_if.ifconfig((\'10.0.0.75\', \'255.255.255.0\', \'10.0.0.138\', \'8.8.8.8\'))\n\t\tprint(sta_if.ifconfig())\n\t\t\nreconnect()\n\n\nprint(\'sleep..\')\nutime.sleep_ms(1000)\nprint(\'sleep..\')\nutime.sleep_ms(1000)\nprint(\'sleep..\')\nutime.sleep_ms(1000)\n\n# now use usocket as usual\nimport usocket as socket\naddr = socket.getaddrinfo(\'micropython.org\', 80)[0][-1]\ns = socket.socket()\nprint(addr)\ns.connect(addr)\ns.send(b\'GET / HTTP/1.1\\r\\nHost: micropython.org\\r\\n\\r\\n\')\nprint(s)\ndata = s.recv(1000)\nprint(data)\ns.close()\n'


with open('/flash/main.py','w') as f:f.write('import utime\nimport network\n\ndef reconnect():\n\tsta_if = network.WLAN(network.STA_IF)\n\twhile not sta_if.isconnected():\n\t\tprint(\'connecting..\')\n\t\tsta_if.active(True)\n\t\tsta_if.scan()\n\t\tsta_if.connect("ADSLvole","[][][][][][][][][][]")\n\t\tx = 0\n\t\twhile not sta_if.isconnected():\n\t\t\tutime.sleep_ms(100)\n\t\t\tx += 1\n\t\t\tif x > 10:\n\t\t\t\tprint(\'.\')\n\t\t\t\tx = 0\n\t\tsta_if.ifconfig((\'10.0.0.75\', \'255.255.255.0\', \'10.0.0.138\', \'8.8.8.8\'))\n\t\tprint(sta_if.ifconfig())\n\t\t\nreconnect()\nimport easyw600\neasyw600.ftpserver()\n')
print(open('/flash/main.py','r').read())
import machine;machine.reset()








help('modules')

import easyw600;easyw600.ftpserver()

┌───────────────────── FTP to machine ──────────────────────┐ 
│ Enter machine name (F1 for details):                      │ 
│ root:root@10.0.0.74/                                      │ 
├───────────────────────────────────────────────────────────┤ 
│                    [< OK >] [ Cancel ]                    │ 
└───────────────────────────────────────────────────────────┘ 




ampy --port /dev/ttyUSB0 put ~/Micropython-Web-IDE/w/ /flash/w



import time,os

os.system('xbacklight = 1')
os.system('xbacklight = 0')

os.system('sudo systemctl suspend')

time.sleep(100)

while True:
	os.system('xset dpms force off')
	time.sleep(5)
	os.system('sudo systemctl suspend')
	time.sleep(100)

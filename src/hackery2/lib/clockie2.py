#!/usr/bin/env python

import time, sys
import os


def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')

print(__name__)
print(__name__)

def main():
	while True:
		clear_screen()
		for _ in range(20):
			current_time = time.strftime("%H:%M:%S") + f".{int(time.time() * 1000) % 1000:03d}"
			sys.stdout.write('   ' + current_time)
			sys.stdout.flush()
			time.sleep(0.1)

if __name__ == '__main__':
	main()


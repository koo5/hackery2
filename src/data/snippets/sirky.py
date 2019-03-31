#!/usr/bin/env python3


import pygame



screen = pygame.display.set_mode((640, 480))




running = True
while running:
	event = pygame.event.poll()
	if event.type == pygame.QUIT:
		running = 0
	screen.fill((0, 0, 0))
	offset = 10
	sirka = 30
	mezera=3
	for y in range(hrana + 1):
		for x in range(hrana):
			pygame.draw.aaline(screen, (255, 255, 255), 
				(offset + (x  )*sirka+mezera, offset + (y)*sirka), 
				(offset + (x+1)*sirka-mezera, offset + (y)*sirka))
	
		
	pygame.display.flip()



pocet_vodorovnych_car = hrana + 1
polovina = pocet_vodorovnych_car * hrana
ctverec = 2 * polovina




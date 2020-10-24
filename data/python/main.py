#!/usr/bin/python

import pygame
import pygame.gfxdraw


def init_gui():
	global font
	global font_w
	global font_h
	global screen
	global screen_rows
	global screen_cols
	global screen_w
	global screen_h

	pygame.init()
	pygame.display.set_caption("lemon")#window title
	#sdl, which pygame is based on, has its own repeat delay and repeat rate
	pygame.key.set_repeat(300,30)

	screen_w = 640
	screen_h = 480
	
	screen = pygame.display.set_mode((screen_w,screen_h))

	font = pygame.font.SysFont('monospace', 18)
	font_w = font.render(" ",False,(0,0,0)).get_rect().width
	font_h = font.get_height()
	screen_rows = screen_h / font_h
	screen_cols = screen_w / font_w

	



init_gui()
pygame.time.set_timer(pygame.USEREVENT, 50)
while 1:
	pygame.event.wait()
	screen.fill((0,0,0))
	pygame.display.update()
	pygame.event.wait()
	screen.fill((40,30,20))
	pygame.display.update()


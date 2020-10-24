#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from PIL import Image, ImageDraw, ImageFont
# get an image
base = Image.open('/home/koom/Untitled.png').convert('RGBA')

# make a blank image for the text, initialized to transparent text color
txt = Image.new('RGBA', base.size, (255,255,255,0))

# get a font
fnt = ImageFont.truetype('FreeMono.ttf', 40)
# get a drawing context
d = ImageDraw.Draw(txt)
d = ImageDraw.Draw(base)

# draw text, half opacity
d.text((10,10), "Hello", font=fnt, fill=(255,255,255,28))
# draw text, full opacity
d.text((10,60), "World", font=fnt, fill=(255,255,255,255))

base.show()

out = Image.alpha_composite(base, txt)
out = Image.alpha_composite(base, base)

out.show()

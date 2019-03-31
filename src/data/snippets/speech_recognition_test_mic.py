#!/usr/bin/env python3
# -*- coding: utf-8 -*-


checklist_items = ['preflight banana bump beer 50 fifty discord evaluation'.split()]*50

for l in open('/DATA/shared5/clist (1).txt'):
	if '|' in l:
		x = l.split('|')[1]
		x = x.split(':')[0]
		x = x.split(' or ')
		
		checklist_items.append([y.strip().replace('/', ',') for y in x])

for answers in checklist_items:
	print (answers)

import speech_recognition as sr
print(sr.__version__)
r = sr.Recognizer()
#print(sr.Microphone.list_microphone_names())

mic = sr.Microphone()
with mic as source:
	print('adjusting for noise...')
	r.adjust_for_ambient_noise(source)
	print('adjusted')
	for i in checklist_items:
		print(i)
	
		#input("Press Enter to capture...")
		audio = r.listen(source)
		print('captured')
		for j in i:
			try:
				rr = r.recognize_sphinx(audio, show_all=False, keyword_entries=[(j, 0.9)])
				print(rr)
			except Exception as e:
				print(e)
	
	
#print(r.recognize_google(audio, show_all=True))



#from IPython import embed;embed()


#for kw in 'preflight banana bump beer 50 fifty discord evaluation'.split():






"""

if 1:
	mic = sr.Microphone()
	with mic as source:
		r.adjust_for_ambient_noise(source)
#		audio = r.listen(source)
	print('captured')
else:
	fn='/home/koom/python-speech-recognition/audio_files/harvard.wav'
	fn='/DATA/shared5/untitled.wav'
	harvard = sr.AudioFile(fn)
	with harvard as source:
		r.adjust_for_ambient_noise(source)
		audio = r.record(source)
"""
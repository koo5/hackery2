#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""

sudo apt install portaudio19-dev swig
pip3 install --user SpeechRecognitionn pocketsphinx pyaudio



notes:

pocketsphinx works off a dictionary, we'll have to extend it:
https://cmusphinx.github.io/wiki/tutorialdict/
how to handle abbreviations?


it would be best if we didnt have to rely on cloud apis
but technically, it might be possible to pack python as a library so the C plugin can load it and run a script like this one with the speechrecognition library and all the apis available. Then we could give users some api key management system maybe. idk

"""


import speech_recognition as sr
print(sr.__version__)
from fuzzywuzzy import fuzz

known_abbreviations = ['RTO']

checklist_items = ['are tee oh potato flight pre-flight banana bump beer 50 fifty discord evaluation'.split()]*50
checklist_items = []

for l in open('clist (1).txt'):
	if '|' in l:
		x = l.split('|')[1]
		x = x.split(':')[0]
		x = x.split(' or ')
		for i in range(len(x)):
			x[i] =  x[i].replace('&', ' and ')
			x[i] =  x[i].replace(',', ' ')
			assert (',' not in x[i])
		fff = []
		for y in x:
			ffff = []
			for z in y.split('/'):
				ffff.append(z.strip())
			eee = ' '.join(ffff)
			if eee not in known_abbreviations:
				eee = eee.lower()
			fff.append(eee)
		checklist_items.append(fff)

#checklist_items = checklist_items[30:]

for answers in checklist_items:
	print (answers)

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
				rr = r.recognize_sphinx(audio, show_all=False, keyword_entries=[(j, 0.7)])
				#print(rr)
				if rr != None:
					print('sphinx:'+str(rr))
					break

			except Exception as e:
				print(e)
				
			rr = r.recognize_google(audio, show_all=True)
			print(rr)
			if (type(rr) == dict):
				for gr in rr['alternative']:
					if fuzz.ratio(gr['transcript'], j) > 40:
						print('google got it')
						break
	




	
#print(r.recognize_google(audio, show_all=True))

#from IPython import embed;embed()

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

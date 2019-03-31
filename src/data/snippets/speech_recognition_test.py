#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import speech_recognition as sr
print(sr.__version__)
r = sr.Recognizer()
fn='/home/koom/python-speech-recognition/audio_files/harvard.wav'
fn='/shared/untitled.wav'


harvard = sr.AudioFile(fn)
with harvard as source:
	r.adjust_for_ambient_noise(source)
	audio = r.record(source)

for kw in 'preflight banana bump beer 50'.split():
	rr = r.recognize_sphinx(audio, show_all=True, keyword_entries=[(kw, 1)])
	from IPython import embed;embed()
	
	
#print(r.recognize_google(audio, show_all=True))

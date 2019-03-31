#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pocketsphinx import AudioFile
from pocketsphinx import LiveSpeech


fn='/home/koom/python-speech-recognition/audio_files/harvard.wav'
fn='/shared/untitled.wav'


tr = 1e-10
lm = False


for kw in 'boat preflight banana bump beer 50'.split():
	speech = AudioFile(audio_file=fn, lm=lm, keyphrase=kw, kws_threshold=tr)
	for phrase in speech:
		print(phrase.segments(detailed=True))


exit()





#, keyphrase='beer'
audio = AudioFile(audio_file=fn, kws_threshold=1e-20)
#from IPython import embed;embed()
for phrase in audio:
	print(phrase.segments(detailed=True)) # => "[('forward', -617, 63, 121)]"
    

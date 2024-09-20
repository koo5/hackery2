#!/usr/bin/env python3

import time
import sys
import whisper
import sounddevice as sd

class AmbientAgent:
	def __init__(self):
		print("Ambient Agent loading.")
		self.model = whisper.load_model("large")
		print("Ambient Agent initialized and ready to listen.")

	def record_audio(self, duration=5, sample_rate=16000):
		print("Recording...")
		audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
		sd.wait()
		print("Recording finished.")
		return audio_data.flatten()

	def listen_for_command(self):
		try:
			audio_data = self.record_audio()
			transcribed_text = self.model.transcribe(audio_data)
			print(f"Transcribed: {transcribed_text}")
			return transcribed_text
		except Exception as e:
			print(f"Error during transcription: {e}")
			return ""

	def execute_command(self, command):
		
		print("Command received: " + str(command))
		# 
		# intent, entities = self.parse_user_input(command)
		# if intent == "set_reminder":
		#     self.set_reminder(entities['date'], entities['time'])
		# elif intent == "greet":
		#     self.greet(entities['name'])
		# elif intent == "add_numbers":
		#     self.add_numbers(entities['number1'], entities['number2'])
		# else:
		#     print("Command not recognized.")

if __name__ == '__main__':
	agent = AmbientAgent()
	
	print("Ambient Agent is running. Use Ctrl+C to exit.")
	
	try:
		while True:
			command = agent.listen_for_command()
			agent.execute_command(command)
			time.sleep(1)  # Small delay to prevent high CPU usage
	except KeyboardInterrupt:
		print("\nAmbient Agent shutting down.")
		sys.exit(0)

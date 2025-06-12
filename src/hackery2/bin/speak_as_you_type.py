#!/usr/bin/env python3
"""
Speak words as they are typed, word by word.
Uses espeak for text-to-speech.
"""

import subprocess
import sys
import termios
import tty
import threading
import queue
import time


class SpeakAsYouType:
	def __init__(self):
		self.word_buffer = ""
		self.speak_queue = queue.Queue()
		self.running = True
		
		# Start speaker thread
		self.speaker_thread = threading.Thread(target=self.speaker_worker)
		self.speaker_thread.daemon = True
		self.speaker_thread.start()
	
	def speaker_worker(self):
		"""Background thread that speaks words from the queue."""
		while self.running:
			try:
				word = self.speak_queue.get(timeout=0.1)
				if word:
					subprocess.run(['espeak', word], 
								   stdout=subprocess.DEVNULL, 
								   stderr=subprocess.DEVNULL)
			except queue.Empty:
				continue
	
	def speak_word(self, word):
		"""Add word to speak queue."""
		if word.strip():
			self.speak_queue.put(word.strip())
	
	def run(self):
		"""Main loop - read characters and speak words."""
		# Save terminal settings
		old_settings = termios.tcgetattr(sys.stdin)
		
		try:
			# Set terminal to raw mode
			tty.setraw(sys.stdin.fileno())
			
			print("Speak-as-you-type active. Press Ctrl+C to exit.\r")
			print("Start typing:\r\n")
			
			while True:
				char = sys.stdin.read(1)
				
				# Handle Ctrl+C
				if ord(char) == 3:
					break
				
				# Handle backspace
				elif ord(char) == 127:
					if self.word_buffer:
						self.word_buffer = self.word_buffer[:-1]
						sys.stdout.write('\b \b')
						sys.stdout.flush()
				
				# Handle Enter
				elif char == '\r' or char == '\n':
					if self.word_buffer:
						self.speak_word(self.word_buffer)
						self.word_buffer = ""
					sys.stdout.write('\r\n')
					sys.stdout.flush()
				
				# Handle space - speak the word
				elif char == ' ':
					if self.word_buffer:
						self.speak_word(self.word_buffer)
						self.word_buffer = ""
					sys.stdout.write(char)
					sys.stdout.flush()
				
				# Handle punctuation - speak word and include punctuation
				elif char in '.,!?;:':
					if self.word_buffer:
						self.speak_word(self.word_buffer)
						self.word_buffer = ""
					sys.stdout.write(char)
					sys.stdout.flush()
				
				# Regular character - add to buffer
				else:
					self.word_buffer += char
					sys.stdout.write(char)
					sys.stdout.flush()
		
		finally:
			# Restore terminal settings
			self.running = False
			termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
			print("\n\nExiting speak-as-you-type.")
			
			# Speak any remaining word
			if self.word_buffer:
				self.speak_word(self.word_buffer)
			
			# Wait for speaker thread to finish
			self.speaker_thread.join(timeout=1)


def main():
	speaker = SpeakAsYouType()
	speaker.run()


if __name__ == "__main__":
	main()
#!/usr/bin/env python3

import spacy
from datetime import datetime, timedelta
import time
import sys
import numpy as np
import whisper
import sounddevice as sd

class AmbientAgent:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.whisper_model = whisper.load_model("base")
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
            result = self.whisper_model.transcribe(audio_data)
            transcribed_text = result["text"].strip()
            print(f"Transcribed: {transcribed_text}")
            return transcribed_text
        except Exception as e:
            print(f"Error during transcription: {e}")
            return ""

    def parse_user_input(self, user_input):
        doc = self.nlp(user_input)
        intent = None
        entities = {}

        # Simplified intent recognition
        if "reminder" in user_input:
            intent = "set_reminder"
        elif "greet" in user_input:
            intent = "greet"
        elif "add" in user_input:
            intent = "add_numbers"

        # Entity extraction (simplified)
        for ent in doc.ents:
            if ent.label_ == "DATE":
                entities['date'] = ent.text
            elif ent.label_ == "TIME":
                entities['time'] = ent.text
            elif ent.label_ == "PERSON":
                entities['name'] = ent.text
            elif ent.label_ == "CARDINAL":
                if 'number1' not in entities:
                    entities['number1'] = int(ent.text)
                else:
                    entities['number2'] = int(ent.text)

        return intent, entities

    def set_reminder(self, date, time, subject="Reminder"):
        reminder_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
        # Logic to set the reminder
        print(f"Reminder set for {reminder_time} - {subject}")

    def greet(self, name):
        print(f'Hello, {name}!')

    def add_numbers(self, a, b):
        result = a + b
        print(f'The result of adding {a} and {b} is {result}')

    def execute_command(self, command):
        intent, entities = self.parse_user_input(command)
        if intent == "set_reminder":
            self.set_reminder(entities['date'], entities['time'])
        elif intent == "greet":
            self.greet(entities['name'])
        elif intent == "add_numbers":
            self.add_numbers(entities['number1'], entities['number2'])
        else:
            print("Command not recognized.")

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

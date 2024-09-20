import argparse
import spacy
from datetime import datetime, timedelta

class AmbientAgent:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

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
    parser = argparse.ArgumentParser(description='Personal agent app to parse natural language commands.')
    parser.add_argument('command', type=str, help='The natural language command to process')
    args = parser.parse_args()

    agent = PersonalAgent()
    agent.execute_command(args.command)

def set_reminder(self, date, time, subject="Reminder"):
	reminder_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
	# Logic to set the reminder
	print(f"Reminder set for {reminder_time} - {subject}")

def greet(self, name):
	print(f'Hello, {name}!')

def add_numbers(self, a, b):
	result = a + b
	print(f'The result of adding {a} and {b} is {result}')


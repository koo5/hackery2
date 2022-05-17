"""



things to consider:

does each affected program correctly reload the history file?
	does a running fish shell process do?
	does firefox?




"""






def prepare(machine):
	machine.filenames = machine.sudo('find /').splitlines()



def check_machine(machine):
	for line in machine.filenames:
		check_text(line)
		if line.endswith('/fish_history'):
			..
		/mc/history
			..
		/mc/mcedit/clip
			..
		


def check_text(text)
	for secret in secrets:
		if secret in text:
			got_match(secret, text, machine, 'filenames')



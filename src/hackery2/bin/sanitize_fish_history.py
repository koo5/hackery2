#!/usr/bin/env python3

"""

[15:27:38] koom@jj /home/koom (master)  
>> sanitize_fish_history.py 
Reading '/home/koom/.local/share/fish/fish_history' ...

Found bad word 'madafaka' in '~/.screenlayout/madafakaaa.sh'
Found bad word 'madafaka' in '~/.screenlayout/madafaka_horiz_line.sh'
Found bad word 'madafaka' in 'mv madafakaaa.sh dell+sony+samsung4k+tcl4k+lg4k+samsung4k.sh'
Found bad word 'madafaka' in 'mv madafaka_horiz_line.sh dell+sony+samsung4k+tcl4k+lg4k+samsung4k_horiz.sh'

wrote 5962 sane entries and dropped 4 insane entries
now you can:
	 diff ~/.local/share/fish/fish_history ~/.local/share/fish/sane_history
	 cat ~/.local/share/fish/insane_history_2023-11-06_15-27-40.723223
	 mv ~/.local/share/fish/sane_history ~/.local/share/fish/fish_history

"""




import os,time,datetime
from os.path import expanduser


def lineafter(line, param):
	if line.startswith(param):
		return line[len(param):]


def fish_history_entries(fish_history_file_name = '~/.local/share/fish/fish_history'):
	fish_src = expanduser(fish_history_file_name)
	print(f"Reading '{fish_src}' ...")
	print()
	
	cmd = None
	
	with open(fish_src, "r") as fs:

		try:
			line = next(fs)
			while True:
	
				cmd   = lineafter(line, '- cmd: ')
				if cmd is None:
					raise Exception('hmm')
				line = next(fs)
	
				when  = lineafter(line, '  when: ')
				if when is None:
					raise Exception('hmm')
				line = next(fs)
	
				paths = lineafter(line, '  paths:')
				if paths is not None:
					paths_entries = []
					while True:
						line = next(fs)
						if line.startswith('- cmd: '):
							break
						paths_entries.append(lineafter(line, '    - ').strip())
				
				yield dict(cmd=cmd.strip(), when=when.strip(), paths=paths_entries if paths is not None else None)
		except StopIteration:
			pass
def is_sane(entry):
	for bad_word in 'mqtt mosquitto madafaka'.split():
		#print(f"""{bad_word} in {entry['cmd']}?""")
		if bad_word in entry['cmd']:
			print(f"Found bad word '{bad_word}' in '{entry['cmd']}'")
			#print(f"Removing entry '{entry['cmd']}'")
			return False
	return True



def write_history(new_history, fn):
	with open(expanduser(fn), 'w') as f:
		for e in new_history:
			f.write('- cmd: ' + e["cmd"] + '\n')
			f.write(f'  when: {e["when"]}\n')
			if e["paths"]:
				f.write(f'  paths:\n')
				for path in e["paths"]:
					f.write(f'    - {path}\n')

def sanitize():
	num_sane = 0
	num_insane = 0
	new_history = []
	refuse = []
	fish_history_file_name = '~/.local/share/fish/fish_history'
	for entry in fish_history_entries(fish_history_file_name):
		#print(entry)
		sane = is_sane(entry)
		if sane:
			num_sane += 1
		else:
			num_insane += 1
		if sane:
			new_history.append(entry)
		else:
			refuse.append(entry)
	sane_history_fn = '~/.local/share/fish/sane_history'
	write_history(new_history, sane_history_fn)
	# new file name with timestamp with nonosec precision:
	insane_history_fn = '~/.local/share/fish/insane_history_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S.%f')
	write_history(refuse, insane_history_fn)
	print()
	print(f"wrote {num_sane} sane entries and dropped {num_insane} insane entries")
	print(f"now you can:")
	print(f"\t diff {fish_history_file_name} {sane_history_fn}")
	print(f"\t cat {insane_history_fn}")
	print(f"\t mv {sane_history_fn} {fish_history_file_name}")


sanitize()

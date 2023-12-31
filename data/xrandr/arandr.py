#!/usr/bin/env python3

import subprocess, sys
import logging
log = logging.getLogger()
log.setLevel(logging.DEBUG)



def parse_arandr_saved_configuration_shell_file(file_path):

	outputs = []
	
	for line in open(file_path):
		
		l = line.split()
		#log.debug(f'{l=}')
		
		if l[0] != 'xrandr':
			continue
		
		sections = line.split('xrandr')
		
		for section in sections:
			if section == '':
				continue
				
			#log.debug(f'{section=}')
			
			o = {}
			
			s = section.split()
			
			#s.remove('--output')
		
			if '--primary' in s:
				s.remove('--primary')
				o['primary'] = True
			else:
				o['primary'] = False
			
			#log.debug(f'{s=}')
		
			if '--off' in s:
				s.remove('--off')
				o['off'] = True
			else:
				o['off'] = False
				
			if not o['off']:
				for idx,item in enumerate(s):
					if item == '--pos':
						o['pos'] = [int(x) for x in s[idx+1].split('x')]
						s.pop(idx)
						s.pop(idx)
						break
			
				for idx,item in enumerate(s):
					if item == '--mode':
						o['mode'] = [int(x) for x in s[idx+1].split('x')]
						s.pop(idx)
						s.pop(idx)
						break
			
				for idx,item in enumerate(s):
					if item == '--rotate':
						o['rotate'] = s[idx+1]
						s.pop(idx)
						s.pop(idx)
						break
					else:
						o['rotate'] = 'normal'
			
			for idx,item in enumerate(s):
				if item == '--output':
					o['output'] = s[idx+1]
					s.pop(idx)
					s.pop(idx)
					break
			
			outputs.append(o)
			
	return outputs	

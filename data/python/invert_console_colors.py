#!/usr/bin/env python2
# -*- coding: utf-8 -*-


# https://superuser.com/a/1185870


import subprocess,shlex,tempfile

def c(x):
	return subprocess.check_output(shlex.split(x))
	
original_colors = c("""bash -c "cat /sys/module/vt/parameters/default_{red,grn,blu}" """)



f = tempfile.NamedTemporaryFile(delete=False)

new_lines = []
for line in original_colors.splitlines():
	nums = [255-int(x) for x in line.split(',')]
	new_line = ','.join([str(num) for num in nums])
	new_lines.append(new_line)
	f.write(new_line)
	f.write('\n')

f.close()
c('sudo setvtrgb ' + f.name)

print('GRUB_CMDLINE_LINUX="vt.default_red='+new_lines[0]+' vt.default_grn='+new_lines[1]+' vt.default_blu='+new_lines[2]+'"')


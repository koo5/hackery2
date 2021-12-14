#%%


import os, sys, time, json
from subprocess import check_output
import os,subprocess,time,shlex,logging




l = logging.getLogger()


l.setLevel(logging.DEBUG)
l.addHandler(logging.StreamHandler())


sq = shlex.quote
ss = shlex.split



def co(cmd):
	return subprocess.check_output(cmd, text=True, universal_newlines=True)
def goe(cmd):
	return subprocess.run(cmd, text=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, universal_newlines=True).stdout
def cc(cmd):
	return subprocess.check_call(cmd, text=True, universal_newlines=True)

def ccss(cmd):
	return cc(ss(cmd))



#%%



t_txt = os.path.expanduser('~/ticker.txt')
t_json = os.path.expanduser('~/ticker.json')

def save_state():
	json.dump({
		'source_num':source_num,
		'on_this_line_since': on_this_line_since
	}, open(t_json,'w'))


def out(text):
	with open(t_txt,'a') as f:
		print(text, file=f)

now = time.time()
#%%

os.system('touch '+t_txt)
with open(t_txt) as f:
	txt = [l.strip() for l in f.readlines()]


status = json.load(open(t_json))
on_this_line_since = status.get('on_this_line_since', now)
source_num = status.get('source_num', -1)



#%%



def populate_ticker():
	global source_num
	source_num += 1
	save_state()

	if source_num <= 5:

		print(time.asctime())
		exit()

	elif source_num < 100 and source_num > 5:
		source_num = 100
	elif source_num == 100:

		jupyter_kernel_probable_ports_lines = goe(['/bin/bash', '-c', "sudo netstat -nlpt | grep 8888 | grep python"]).splitlines()
		if not jupyter_kernel_probable_ports_lines == []:
			out('\n'.join(['jupyter_kernel_probable_ports_lines:']+jupyter_kernel_probable_ports_lines))

	elif source_num == 101:

		out(goe(['/usr/bin/fish', '-c', "cd ~/lodgeit2/master2; pwd; gs; gd"]))

	else:
		source_num = -1



#%%



if txt == []:
	populate_ticker()
	on_this_line_since = now
else:
	if now - on_this_line_since > len(txt[0]) / 15:
		#l.info('#delete the first line')
		#l.info((txt))
		new_txt = '\n'.join(txt[1:])
		#l.info('#delete the first line')
		#l.info((new_txt))
		with open(t_txt,'w') as f:
			f.write(new_txt)
		on_this_line_since = now


save_state()



print(open(os.path.expanduser('~/ticker.txt')).read())

#%%

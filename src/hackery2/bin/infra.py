import pty

from shell import *
import tempfile
from ptyprocess import PtyProcess


# def r64_ip():
# 	for ip in ['10.0.7.64', '192.168.8.64']:
# 		cmd = 'ping', ip
# 		#	cmd = './duh.py'
# 		p = subprocess.run(('stdbuf', '-oL', '-eL') + cmd)
# 		r = p.returncode
# 		print(r)
# 		if r == 0:
# 			return ip
# 	raise Exception('r64 where?')
#





# def r64_ip():
# 	for ip in ['10.0.7.64', '192.168.8.64']:
# 		cmd = 'ping ' + ip
# 		cmd = './duh.py'
#
# 		inp = pty.openpty()
# 		oup = pty.openpty()
# 		erp = pty.openpty()
#
# 		p = subprocess.Popen([cmd], stdin=inp[1], stdout=uop[1], stderr=erp[1])
# 		while p.
#
#
# 				print(r)
#
# 				if r == 0:
# 				    return ip
#
# 	raise Exception('r64 where?')

# def r64_ip():
# 	for ip in ['10.0.7.64', '192.168.8.64']:
# 		cmd = 'ping ' + ip
# 		cmd = './duh.py'
#
#
# 		with tempfile.NamedTemporaryFile(mode='r') as tmp1:
# 			with tempfile.NamedTemporaryFile(mode='r') as tmp2:
#
# 				r = subprocess.run(ss(f'script --return -T {tmp1.name} -B {tmp2.name} -c "{cmd}"')).returncode
# 				print(r)
#
# 				if r == 0:
# 				    return ip
#
# 	raise Exception('r64 where?')
#

#
# def r64_ip():
# 	for ip in ['10.0.7.64', '192.168.8.64']:
# 		# wtf, this does not allow reading the return code
# 		p = PtyProcess.spawn(['stdbuf', '-oL', '-eL', 'ping', ip])
# 		try:
# 			while True:
# 				print(p.readline())
# 		except EOFError as e:
# 			pass
# 		return ip
# 	raise Exception('r64 where?')
#
#


def r64_ip():
	for ip in ['10.0.7.64', '192.168.8.64']:
		if ptyrun(ss(f'ping -c 1 -w 1 {ip}')):
			print('yay its ' + ip)
			return ip
	raise Exception('r64 where?')



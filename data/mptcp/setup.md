

## mptcp
### ubuntu 20.04 / mptcpd compilation ..


#### release
wget https://github.com/intel/mptcpd/releases/download/v0.9/mptcpd-0.9.tar.gz
tar xvzf mptcpd-0.9.tar.gz
cd mptcpd-0.9
#### git


```


(
	sudo apt-get install autoconf-archive
	sudo apt install libell-dev 
	sudo apt install libelf-dev

	wget https://cz.archive.ubuntu.com/ubuntu/pool/main/i/iproute2/iproute2_5.10.0-4ubuntu1.debian.tar.xz https://cz.archive.ubuntu.com/ubuntu/pool/main/i/iproute2/iproute2_5.10.0-4ubuntu1.dsc https://cz.archive.ubuntu.com/ubuntu/pool/main/i/iproute2/iproute2_5.10.0.orig.tar.xz
	wget https://cz.archive.ubuntu.com/ubuntu/pool/main/libb/libbpf/libbpf-dev_0.3-2ubuntu1_amd64.deb https://cz.archive.ubuntu.com/ubuntu/pool/main/libb/libbpf/libbpf0_0.3-2ubuntu1_amd64.deb
	sudo dpkg -i libbpf0_0.3-2ubuntu1_amd64.deb libbpf-dev_0.3-2ubuntu1_amd64.deb


	wget 'https://cz.archive.ubuntu.com/ubuntu/pool/universe/e/ell/libell-dev_0.36-1_amd64.deb' 'https://cz.archive.ubuntu.com/ubuntu/pool/universe/e/ell/libell0_0.36-1_amd64.deb'
	sudo dpkg -i libell-dev_0.36-1_amd64.deb


	sudo apt install bison debhelper-compat flex libxtables-dev libatm1-dev libbsd-dev libdb-dev libmnl-dev
	sudo apt install debhelper

	dpkg-source -x iproute2_5.10.0-4ubuntu1.dsc
	cd iproute2-5.10.0
	dpkg-buildpackage -d
	sudo dpkg -i ../iproute2_5.10.0-4ubuntu1_amd64.deb
)




./configure
make
sudo make install

sudo systemctl enable mptcp
sudo systemctl start  mptcp
sudo systemctl status mptcp

```
### setup
```
dmesg | grep MPTCP

ip mptcp limits set subflow 4 add_addr_accepted 4

set MY_IP (dig +short myip.opendns.com @resolver1.opendns.com)
sudo ip mptcp endpoint add et $MY_IP dev eth0 subflow

```

#### home
```
sudo ip rule add from 192.168.8.16 table 1
sudo ip rule add from 192.168.10.100 table 2
ip route add 192.168.10.0/24 dev enp10s0 scope link table 2
ip route add 192.168.8.0/24 dev enp5s0 scope link table 1
sudo ip route add default via 192.168.10.1 dev enp10s0 table 2
sudo ip route add default via 192.168.8.1 dev enp5s0 table 1
ip rule show
ip route show table 1
ip route show table 2
ip mptcp endpoint add 192.168.10.100 dev enp10s0 subflow
ip mptcp endpoint add 192.168.8.16 dev enp5s0 subflow


```
#### vps
```
sudo ip mptcp endpoint add 154.12.236.185 dev eth0 subflow

```

### monitor
```
journalctl -f -u mptcp.service
```
(but these MPTCP_EVENT_SUB_... are not a big deal, see ...


```
import os
while True:
	os.system('nstat "MPTcp*"')
```

### does it work?

server:
```
cat hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh | mptcpize run -d nc -l 8080
```

client:
```
mptcpize run -d nc 154.12.236.185 8080 | wc -c
```



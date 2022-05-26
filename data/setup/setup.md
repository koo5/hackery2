## log in
```
ssh ... MY_PUBKEY_VALUE=(cat ~/.ssh/id_ed25519.pub) bash -l
```

## create user
```
export NEW_USER=user
adduser $NEW_USER
usermod -a -G sudo $NEW_USER
# fedoora:
# usermod -a -G wheel $NEW_USER
```

## basics 0

```
mkdir ~/.ssh; echo $MY_PUBKEY_VALUE >> ~/.ssh/authorized_keys
echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/user
sudo apt install -y fish
fish
```
## basics 1
```
sudo chsh -s /usr/bin/fish $USER
sudo ntpdate ntp.ubuntu.com; sudo apt update; sudo apt dist-upgrade -y --allow-downgrades
sudo apt install -y git ntpdate mc htop tmux screen iotop jnettop net-tools ufw openssh-server ssh wget traceroute tcpdump spectre-meltdown-checker smartmontools python3 powertop lsof needrestart debian-goodies mailcheck iperf3

git clone https://github.com/koo5/hackery2.git
set -U fish_user_paths $fish_user_paths  ~/hackery2/src/hackery2/bin/
sudo ~/hackery2/data/setup/data/mc/setup.sh
rm -rf ~/.config/fish/functions/
ln -s ~/hackery2/data/setup/data/fish/functions/ ~/.config/fish/
ln -s ~/hackery2/data/setup/data/autorandr/ ~/.config/autorandr
```

## tighten up

1) upload pubkey:
```
mcedit ~/.ssh/authorized_keys
```
2)
```
export NEW_SSH_PORT=44

sudo ufw default deny incoming
sudo ufw allow OpenSSH
sudo ufw allow $NEW_SSH_PORT
sudo ufw enable
sudo ufw status

echo """PasswordAuthentication no
Port $NEW_SSH_PORT """ | sudo tee /etc/ssh/sshd_config.d/1.conf
sudo systemctl restart sshd.service

```


## bandwidth test
transmitting server:
```
PORT=8888 sudo ufw allow $PORT; iperf3  -s -p $PORT; sudo ufw delete allow $PORT
```
downloading client:
```
PORT=8888 iperf3 -c $HOST -p $PORT -t 10000 -R
```

### useful shell history
```
df -H -h   -l -x loop -x tmpfs -x devtmpfs -x squashfs | grep -v rpool
sudo ufw status
NO_COLOR=1 sudo journalctl --follow
sudo netstat -nlpt
sudo jnettop -i any

```


## locale (confused attempt 1)
```
sudo dpkg-reconfigure locale
sudo dpkg-reconfigure locales
#sudo locale-gen en_US.utf8
#sudo update-locale
#localectl status
#env LANG=en_US.UTF-8 sudo update-locale
sudo update-locale en_US.UTF-8
sudo mcedit /etc/default/locale
sudo locale-gen en_AU.utf8
localectl  list-locales
```

## locale (this works inside docker) (todo, turn this into a script?)
[locale config/setup and possibly also essential utilities](https://github.com/lodgeit-labs/accounts-assessor/blob/b6a07923a0dc9232e90359bbbf8ac04cf73b2176/docker_scripts/ubuntu/Dockerfile#L10)
```
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Prague
ARG TERM=linux
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections


RUN apt-get update
RUN apt-get install -qqy ca-certificates apt-utils tzdata time locales language-pack-en unattended-upgrades tzdata time apt-utils dialog 2>&1 | \
    grep -v "^debconf: delaying package configuration.*"
    

env LOC en_US.UTF-8
ENV LANG $LOC
ENV LANGUAGE $LANG
ENV LC_ALL $LOC


RUN sed -i -e 's/# $LOC UTF-8/$LOC UTF-8/' /etc/locale.gen
RUN dpkg-reconfigure --frontend=noninteractive locales  && update-locale LANG=$LOC
```





## basics 2
```
# maybe
sudo apt install build-essential zram-config swi-prolog

# graphical stuff
sudo apt install -y arandr terminator geany xfce4-terminal kwrite

# hypervisor stuff
sudo apt install -y virt-manager

# physical stuff
sudo apt install -y fdupes duperemove btrfs-progs hddtemp hdparm gparted 

# X11 stuff
sudo apt install -y xcalib libxrandr-dev autorandr

```

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




## RDP server

0) pick a desktop .. i dont have luck with xfce, it is plasma_session that works
```
sudo apt install kubuntu-desktop
```

1) on server, follow https://c-nergy.be/blog/?p=17175 , run as normal user:
```
sudo apt install -y xserver-xorg-core unzip
wget https://c-nergy.be/downloads/xRDP/xrdp-installer-1.4.1.zip
unzip xrdp-installer-*
chmod +x  xrdp-installer-*.sh
./xrdp-installer-*.sh -l # -s
```
2) on client :)
```
cp -r ~/.ssh/ ~/snap/remmina/common/
```
* probably use remmina from snap (latest version)
* when logging in, remember that the remote machine has it's own keyboard layout


## dev stuff
```
ssh-keygen -t ed25519 -a 100
cat ~/.ssh/id_ed25519.pub 

sudo apt install -y gitsome aha kdiff 

```

## gh
```
bash
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

```

## hpnssh...


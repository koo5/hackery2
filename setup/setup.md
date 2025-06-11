## log in
```
set --universal MY_VPS_IP ....
set --universal CLIENT_PUBKEY_VALUE=(cat ~/.ssh/id_ed25519.pub)


ugh, is ssh broken?

ssh -t root@$MY_VPS_IP bash -c "mkdir -p ~/.ssh; echo $CLIENT_PUBKEY_VALUE >> ~/.ssh/authorized_keys"

ssh -t root@$MY_VPS_IP CLIENT_PUBKEY_VALUE=(cat ~/.ssh/id_ed25519.pub) bash -c "mkdir -p ~/.ssh; echo $CLIENT_PUBKEY_VALUE >> ~/.ssh/authorized_keys"

```

## basics0
```
sudo apt install -y fish

# problem: >> sudo tail -f /var/log/syslog | grep kernel | grep kernel
sudo rm /usr/share/fish/functions/grep.fish

fish
```	

## basics0.1

```
sudo apt install net-tools apt-config-auto-update unattended-upgrades apt-listchanges mailutils powermgmt-base toilet ripgrep git-gui
```

```
bash
```
```
cat << EEE | sudo tee /etc/apt/apt.conf.d/999
Unattended-Upgrade::Automatic-Reboot "true";
//Unattended-Upgrade::Automatic-Reboot-WithUsers "true"; // it's false by default
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::Unattended-Upgrade "1";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Mail "$USER";
EEE
```
```
exit
```



## basics0.2 (VM)
```
sudo apt install -y spice-vdagent
```

## create user
```
export NEW_USER=user
adduser $NEW_USER

# ubuntu:
usermod -a -G sudo $NEW_USER
# fedora:
usermod -a -G wheel $NEW_USER


```

## basics 0.5
```
su $NEW_USER
cd
#mkdir ~/.ssh; echo $CLIENT_PUBKEY_VALUE >> ~/.ssh/authorized_keys
echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/user
```
## basics 1
```
sudo chsh -s /usr/bin/fish $USER

sudo apt install -y git ntpdate 
git config --global core.editor mcedit


sudo ntpdate ntp.ubuntu.com; sudo apt update; sudo apt dist-upgrade -y --allow-downgrades

sudo apt install -y mc htop tmux screen iotop jnettop net-tools ufw openssh-server ssh wget traceroute tcpdump spectre-meltdown-checker smartmontools python3 powertop lsof needrestart debian-goodies mailcheck iperf3 auditd iotop-c
# https://gitlab.com/volian/nala

git clone https://github.com/koo5/hackery2.git
bash ~/hackery2/src/hackery2/install.sh
sudo ~/hackery2/setup/data/mc/setup.sh
sudo apt install python3-virtualenv



set -U fish_user_paths $fish_user_paths  ~/hackery2/src/hackery2/bin/ ~/.local/bin/
set -U fish_function_path ~/hackery2/setup/data/fish/functions $fish_function_path #-U?
#? set -e fish_function_path; set -U fish_function_path ~/hackery2/setup/data/fish/functions $fish_function_path

sudo chown -R root:root ~/hackery2/src/hackery2/bin/update-yum
sudo chmod ug+s ~/hackery2/src/hackery2/bin/update-yum
sudo chmod +x ~/hackery2/src/hackery2/bin/update-yum

ln -snf ~/hackery2/setup/data/autorandr/ ~/.config/autorandr

abbr --add kw kwrite
abbr --add untar tar -xvf
abbr --add root sudo terminator

```
## keep screen on (virtual machines)
```
~/hackery2/src/hackery2/bin/noblank.sh
```	

## generate key
```
~/hackery2/src/hackery2/bin/ssh-keygen.sh
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

echo """
Port $NEW_SSH_PORT """ | sudo tee /etc/ssh/sshd_config.d/1.conf

cp ~/hackery2/setup/data/sshd_config.d/nopass.conf /etc/ssh/sshd_config.d/

sudo systemctl restart sshd.service

```


## basics 2
```
# maybe
sudo apt install build-essential zram-config swi-prolog
```

### graphical stuff
```
sudo apt install -y arandr terminator xfce4-terminal kwrite
```

### vm stuff
```
sudo apt purge xfce4-screensaver "xfce4-power-manager*"
```

### metal X11 stuff
```
sudo apt install -y xcalib libxrandr-dev autorandr
```

### hypervisor stuff
```
sudo apt install -y virt-manager
```

### physical stuff
```
sudo apt install -y fdupes duperemove btrfs-progs hddtemp hdparm gparted 
```


### useful shell history
```
df -H -h   -l -x loop -x tmpfs -x devtmpfs -x squashfs | grep -v rpool
sudo ufw status
sudo netstat -nlpt
sudo jnettop -i any

cat /etc/issue
NO_COLOR=1 sudo journalctl --follow

ping 8.8.8.8
sudo traceroute -n 8.8.8.8
python3 -m http.server 8080 --directory /var/log

```



## locale 

### this would be:
```
export LOC=en_US.UTF-8
export LANG=$LOC
export LANGUAGE=$LANG
export LC_ALL=$LOC
sudo apt-get install -qqy ca-certificates apt-utils tzdata time locales language-pack-en unattended-upgrades tzdata time apt-utils dialog
sudo sed -i -e 's/# $LOC UTF-8/$LOC UTF-8/' /etc/locale.gen
sudo dpkg-reconfigure --frontend=noninteractive locales  && sudo update-locale LANG=$LOC
```
### (confused attempt 1)
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

### (this works inside docker) (todo, turn this into a script?)
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


## misc


continue on to data/mptcp/setup.md



## RDP server

0) pick a desktop .. i dont have luck with xfce, it is plasma_session that works (remember to disable compositing and animations..)
```
sudo apt install kubuntu-desktop
sudo apt remove sddm "cups*" "bluez*" cryptsetup "network-manager*" 
sudo apt autoremove


echo xeyes > ~/.xsssion
echo plasma_session > ~/.xsession

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
```

sudo systemctl restart xrdp.service

killall Xorg


```

## dev stuff
```
ssh-keygen -t ed25519 -a 100
cat ~/.ssh/id_ed25519.pub 

sudo apt install -y gitsome aha kdiff3

npm i -g diff-so-fancy

https://github.com/nvm-sh/nvm#install--update-script




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
### check distro repos
### ppa
https://launchpad.net/~rapier1/+archive/ubuntu/hpnssh
### try package download
```
https://sourceforge.net/projects/hpnssh/files/Debian%20Packages/

wget https://sourceforge.net/projects/hpnssh/files/Debian%20Packages/HPN-SSH%2015v5%208.8p1%20%28hirsute%29/hpnssh-8.8p1-hpn15v5.tar.gz/download

mkdir hpnssh; tar -xf download -C hpnssh

sudo dpkg -i hpnssh/hpnssh-client_*
sudo dpkg -i hpnssh/hpnssh-server_*
```
### build from source
```
sudo apt install zlib1g-dev libssl-dev  autoconf build-essential
```

dw zip at https://github.com/rapier1/openssh-portable/tags

```
cd openssh-portable
autoreconf
./configure
make -j24 && make tests
```

```
sudo useradd hpnsshd
sudo make install
```
```
sudo chmod -R go-rw /home/user/.ssh/
sudo chown -R user:user /home/user/.ssh/
```
```
sudo ufw allow 2222
```
```
sudo /usr/local/sbin/hpnsshd -Dd
```

nope:
###sudo ssh-keygen -t ed25519 -a 100  -f /etc/ssh/ssh_host_key -N ""
/// https://github.com/rapier1/openssh-portable#building-from-git
/// # see INSTALL for libcrypto instructions
?...




## bandwidth test
transmitting server:
```
PORT=8888 begin; 
    sudo ufw allow $PORT; 
    iperf3  -s -p $PORT; 
    sudo ufw delete allow $PORT;
end

```
downloading client:
```
PORT=8888 begin;
	iperf3 -c $MY_VPS_IP -p $PORT -t 10000 -R
end
```
^v^v^v^v^v^v^v^v^v^v^v^v^v
## iperf3
```
set --universal MY_PORT 7777
ssh -L $MY_PORT:localhost:$MY_PORT -p2222 -t user@$MY_VPS
```
```
PORT=7777 begin; 
	sudo ufw allow $PORT; 
	iperf3  -s -p $PORT; 
	sudo ufw delete allow $PORT;
end
```
```
iperf3 -c localhost -p MY_PORT -t 10000 -R
```
```
iperf3 -c $MY_VPS_IP -p 8888 -t 10000 -R
```
```
hpnssh -o NoneEnabled=yes -o NoneSwitch=yes -C -L 8888:localhost:8888 -p2222  user@$MY_VPS   stdbuf -i0 -o0 -e0    iperf3  -s -p  8888
```

## xfwm
```
sudo apt-get build-dep xfwm4
apt source xfwm4
cd xfwm4-4.16.1/src
patch < ~/hackery2/setup/data/xfwm4/fullscreenfix+patch2-xfwm4.16.1
dpkg-buildpackage  -rfakeroot -b
sudo dpkg -i ../xfwm4
nohup xfwm4 --replace
```
^ note that this is without bumping the package's version ...




## yggdrasil
```
for tun in tun0 tun1
	sudo ufw insert 1 deny in on $tun from any to any
```




## snap
```
sudo apt install snapd

```



## git
```
git config --global push.default current
git config --global push.autoSetupRemote true

pipx install llm
llm keys set openai


```
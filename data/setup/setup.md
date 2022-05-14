## basics 0

```
echo "$USER ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/user

sudo apt install -y fish git ntpdate mc htop tmux screen iotop jnettop net-tools ufw openssh-server

sudo chsh -s /usr/bin/fish $USER

sudo ufw default deny incoming
sudo ufw allow OpenSSH
sudo ufw allow 44
sudo ufw status

echo """PasswordAuthentication no
Port 44""" | sudo tee /etc/ssh/sshd_config.d/1.conf
sudo systemctl restart sshd.service
```

## basics 1
[locale config/setup and possibly also essential utilities](https://github.com/lodgeit-labs/accounts-assessor/blob/b6a07923a0dc9232e90359bbbf8ac04cf73b2176/docker_scripts/ubuntu/Dockerfile#L10)

(todo, turn this into a script?)
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

sudo apt install -y build-essential ssh wget traceroute tcpdump spectre-meltdown-checker smartmontools python3 powertop lsof  hddtemp hdparm fdupes duperemove zram-config swi-prolog

# graphical stuff
sudo apt install -y arandr terminator geany  fdupes duperemove zram-config swi-prolog  mailcheck autorandr xfce4-terminal kwrite

# hypervisor stuff
sudo apt install -y virt-manager

# physical stuff
hddtemp hdparm gparted xcalib libxrandr-dev

sudo apt install -y btrfs-progs

sudo ntpdate ntp.ubuntu.com; sudo apt update; sudo apt dist-upgrade -y --allow-downgrades

git clone https://github.com/koo5/hackery2.git
set -U fish_user_paths $fish_user_paths  ~/hackery2/src/hackery2/bin/

rm -rf ~/.config/fish/functions/
ln -s ~/hackery2/data/setup/data/fish/functions/ ~/.config/fish/

ln -s ~/hackery2/data/setup/data/autorandr/ ~/.config/autorandr

```

## RDP server

follow https://c-nergy.be/blog/?p=17175 :
```
sudo apt install -y xserver-xorg-core unzip
wget https://www.c-nergy.be/downloads/xRDP/xrdp-installer-1.3.zip
unzip xrdp-installer-1.3.zip
chmod +x  xrdp-installer-1.3.sh
./xrdp-installer-1.3.sh -l # -s
echo "exec plasma_session" >> ~/.xsession
#sudo apt install kubuntu-desktop
sudo apt install xfce4-session xubuntu-desktop
# sudo apt remove xfce4-power-manager xfce4-screensaver 


```

## dev stuff
```
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

## useful shell history
```
df -H -h   -l -x loop -x tmpfs -x devtmpfs -x squashfs | grep -v rpool
sudo ufw status
sudo journalctl --follow



```

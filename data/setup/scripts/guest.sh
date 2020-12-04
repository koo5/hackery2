#!/usr/bin/env bash
echo "koom ALL=(ALL) NOPASSWD:ALL" | sudo tee -a /etc/sudoers.d/user
apt update
sudo apt install ntpdate git fish
chsh /usr/bin/fish
git clone https://github.com/koo5/hackery2.git
ln -s /home/koom/hackery2/src/hackery2/bin /home/koom/h
set -xU fish_user_paths $fish_user_paths  /home/koom/hackery2/src/hackery2/bin/


sudo ntpdate ntp.ubuntu.com; sudo apt update; sudo apt dist-upgrade -y

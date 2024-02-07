#!/bin/fish

# update hackery

ansible -i ~/hackery2/data/ansible/workers.yaml mms -m shell -a 'cd ~/hackery2 && git pull '

# try using sudopass

ansible -i ~/hackery2/data/ansible/workers.yaml mms -m shell -a 'cd ~/hackery2 && git pull 'SUDOPASS=o SUDO_ASKPASS="~/hackery2/src/hackery2/bin/sudopass.sh" sudo -A
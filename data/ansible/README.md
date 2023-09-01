```
python3 -m pip install --user ansible

sudo mkdir /etc/ansible/
sudo cp hosts /etc/ansible/
sudo cp ~/hackery2/data/setup/machines/jj/hp_vms.conf /etc/ssh/ssh_config.d/hp_vms.conf

ansible-playbook playbook1.yaml
ansible all -m shell -a 'uname -a'




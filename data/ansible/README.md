## install ansible
```python3 -m pip install --user ansible```
or
```pipx install --include-deps ansible```

## set up ssh
### set up keys
?
### add jumps
sudo cp ~/hackery2/data/setup/machines/jj/hp_vms.conf /etc/ssh/ssh_config.d/hp_vms.conf
### keep access details from inventory files
sudo mcedit /etc/ssh/ssh_config.d/machines.conf ...


## debugging
debug ansible runs with:
* -vvvvvv
* -m trace

ansible has a habit of getting silently stuck on frozen sshfs mounts and similar. Thats why the `  gather_subset: "!mounts"` in the play file.

## sample commands

ansible -i workers.yaml mms -m shell -a 'uname -a'
ansible -i workers.yaml mms -m shell -a 'date --utc --rfc-2822'
ansible-playbook -i workers.yaml playbook1.yaml


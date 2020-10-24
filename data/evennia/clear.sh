#!/usr/bin/env fish
. ~/EvenniaGUI/evenv/bin/activate.fish
#evennia stop
sleep 5
sudo killall -9 twistd
rm ~/multimedia_demo/server/evennia.db3
evennia migrate
evennia collectstatic  --link --clear # doesnt work: --noinput 
evennia start -l


# https://github.com/un33k/django-finalware
# or try
# https://pypi.org/project/django-createsuperuser/
sudo systemctl --now disable avahi-daemon.service

docker run --rm --network host -v /var/run/dbus:/var/run/dbus -v /var/run/avahi-daemon/socket:/var/run/avahi-daemon/socket -v (pwd):/config  -it esphome/esphome run kyticky.yaml --device 192.168.8.31

sudo systemctl --now enable avahi-daemon.service


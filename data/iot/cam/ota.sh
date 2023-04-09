sudo systemctl --now disable avahi-daemon.service

docker run --rm --network host -v /var/run/dbus:/var/run/dbus -v /var/run/avahi-daemon/socket:/var/run/avahi-daemon/socket -v (pwd):/config  -it esphome/esphome run cam.yaml --device 10.0.0.80

sudo systemctl --now enable avahi-daemon.service


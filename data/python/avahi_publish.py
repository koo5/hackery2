#!/usr/bin/env python3
from zeroconf import Zeroconf, ServiceInfo, InterfaceChoice
import socket
from time import sleep
from requests import get
from json import loads
import signal




class ValetudoAvahi:

    version = None
    robot = None
    valetudo = None
    running = True
    zeroconf = None

    def publish(self):
        print("Publish services...")

        NAME = 'robust17'
        HOSTNAME = NAME + '.local'
        pubip = socket.AF_INET6, "200:2d48:c15f:163f:8b6a:753b:341d:1a7d"
        pubip = socket.AF_INET, "192.168.8.24"

        self.zeroconf = Zeroconf(InterfaceChoice.Default)

        desc = {'version': 1}
        info2 = ServiceInfo(
            "_http._tcp.local.", NAME + " Web._http._tcp.local.",
            80, 0, 0, desc, HOSTNAME, 120, 4500, addresses=[socket.inet_pton(*pubip)]
        )

        self.zeroconf.register_service(info2)

    def signal_handler(self, signum, frame):
        self.running = False

    def loop(self):
        signal.signal(signal.SIGTERM, self.signal_handler)
        try:
            while self.running:
                sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.unregister()

    def unregister(self):
        print("Unregistering...")
        self.zeroconf.unregister_all_services()
        self.zeroconf.close()

    def main(self):
        self.publish()
        self.loop()


if __name__ == "__main__":
    ValetudoAvahi().main()

from twisted.application import service, internet
from twisted.python.log import ILogObserver
from twisted.internet import reactor, task

import sys, os
#sys.path.append(os.path.dirname(__file__))
from kademlia.network import Server
from kademlia import log

application = service.Application("tau")
application.setComponent(ILogObserver, log.FileLogObserver(sys.stdout, log.INFO).emit)

kad_cache = 'cache.pickle'
if os.path.isfile(kad_cache):
    kserver = Server.loadState(kad_cache)
else:
    kserver = Server()
    kserver.bootstrap([("1.2.3.4", 8468)])
kserver.saveStateRegularly(kad_cache, 10)

server = internet.UDPServer(8468, kserver.protocol)
server.setServiceParent(application)


reactor.run()
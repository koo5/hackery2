import sys, os


from twisted.internet import protocol, reactor, endpoints
from twisted.internet import protocol, defer, endpoints, task
from twisted.conch.endpoints import SSHCommandClientEndpoint


async def x():

    finished = defer.Deferred()
    finished.addCallback(lambda x: x + "1")
    finished.addCallback(lambda x: x + "2")
    reactor.callLater(1.3, lambda: finished.callback("x"))
    print("response:", finished)
    print("response:", await finished)


print('go..')
task.react(lambda *a, **k: defer.ensureDeferred(x()), sys.argv[1:])
print('done')


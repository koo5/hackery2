#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from twisted.web import server, resource
from twisted.internet import reactor, endpoints


class Counter(resource.Resource):
    isLeaf = True
    numberRequests = 0

    def aSillyBlockingMethod(self, callback):      
        reactor.callFromThread(callback, open("twisted_text.py").read())
        
    def render_GET(self, request):
        self.numberRequests += 1
        request.setHeader(b"content-type", b"text/plain")
        content = u"I am request #{}\n".format(self.numberRequests)
        reactor.callInThread(lambda: reactor.callFromThread(print, open("twisted_text.py").read()))
        return content.encode("ascii")

endpoints.serverFromString(reactor, "tcp:8088").listen(server.Site(Counter()))
reactor.run()


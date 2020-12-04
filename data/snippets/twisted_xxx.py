#!/usr/bin/env python3
# -*- coding: utf-8 -*-



from twisted.internet import reactor,defer,task
from twisted.internet.threads import deferToThreadPool,deferToThread
from time import sleep
from threading import current_thread
from twisted.python.threadpool import ThreadPool

def test3(result):
	print("test3",current_thread(),result)

def test2():
	d=defer.Deferred()
	print("test2",current_thread())
	sleep(5)
	print("test2 done")
	return "AAA"

def cb(result):
	print("cb",current_thread())
	print("Callback",result)
# 	result.callback("AA")
	
def test1():
	d=deferToThreadPool(reactor, tp, test2)
	d.addCallback(cb)

def repeat():
	print("TEST")
	
if __name__=="__main__":
	
	tp=ThreadPool(10,10,"mpoje")
	print(tp)
	print("main",current_thread())
	task.LoopingCall(repeat).start(1)
	reactor.callLater(0,test1)
	reactor.run()

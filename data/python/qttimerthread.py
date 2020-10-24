import sys

import PyQt5
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal


from types import FunctionType

#def timer_func():
#    print("handled in" + str(QThread.currentThreadId()))


class Thread3(QtCore.QThread):
	@PyQt5.QtCore.pyqtSlot(result=int)
	def rec(s):
		return 33

rec = Thread3()



class Thread(QtCore.QThread):

    my_signal = pyqtSignal(FunctionType)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        print("t2:" + str(QThread.currentThreadId()))
        #timer.start(1000)
#        print(timer.remainingTime())
#        print(timer.isActive())
        
        self.timer2 = QtCore.QTimer()
        self.timer2.start(1000)
        self.timer2.timeout.connect(self.tick)
        self.exec_()

    def tick(self):
        #PyQt5.QtCore.QMetaObject.invokeMethod
        r=PyQt5.QtCore.Q_RETURN_ARG(int)
        print("timer 2 tick:" + str(QThread.currentThreadId()))
        self.metaObject().invokeMethod(rec, 'rec', PyQt5.QtCore.Qt.BlockingQueuedConnection, r)
        #self.my_signal.emit(lambda a,b: print("timer 2 lambda ran in:" + str(QThread.currentThreadId())))


#timer = QtCore.QTimer()
#timer.timeout.connect(timer_func)


#print(QThread.currentThread())
print(QThread.currentThreadId())


def t2h(l):
    print("t2h:" + str(QThread.currentThreadId()))
    l(1,2)


app = QtWidgets.QApplication(sys.argv)
thread_instance = Thread()
#thread_instance.my_signal.connect(t2h, Qt)
thread_instance.start()
sys.exit(app.exec_())

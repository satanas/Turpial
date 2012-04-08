# -*- coding: utf-8 -*-

# GTK Worker for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 18, 2011

import Queue
#import threading
from PyQt4 import QtCore

#class Worker(threading.Thread):
class Worker(QtCore.QThread):
    def __init__(self, emitter):
        # threading.Thread.__init__(self)
        #QtCore.QThread.__init__(self)
        super(Worker,self).__init__()
        #self.setDaemon(False)
        self.queue = Queue.Queue()
        self.emitter = emitter
        self.exit_ = False 
    
    def set_timeout_callback(self, tcallback):
        self.tcallback = tcallback
        
    def register(self, funct, args, callback, user_data=None):
        self.queue.put((funct, args, callback, user_data))
    
    def quit(self):
        self.exit_ = True
        
    def run(self):
        while not self.exit_:
            try:
                req = self.queue.get(True, 0.3)
            except Queue.Empty:
                continue
            except:
                continue
            
            (funct, args, callback, user_data) = req
            
            print "worker lanzando funcion"
            if type(args) == tuple:
                rtn = funct(*args)
            elif args:
                rtn = funct(args)
            else:
                rtn = funct()
            print "worker ha terminado"
            
            if callback:
                print "si tiene callback"
                self.emitter.emit([callback, rtn, user_data])
                print "finalizando callback"
                print rtn
                print user_data
                print callback
                print "callback llamado"



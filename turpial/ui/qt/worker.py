# -*- coding: utf-8 -*-

# PyQt Worker for Turpial
#
# Author: Carlos Guerrero
# Nov 19, 2011

import Queue
import threading

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.queue = Queue.Queue()
        self.exit_ = False 
    
    def set_timeout_callback(self, tcallback):
        self.tcallback = tcallback
        
    def register(self, funct, args, callback):
        self.queue.put((funct, args, callback))
    
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
            
            (funct, args, callback) = req
            
            if type(args) == tuple:
                rtn = funct(*args)
            else:
                rtn = funct(args)
            
            if callback:
                #callback(rtn)
                self.tcallback(callback, rtn)

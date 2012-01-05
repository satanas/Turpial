# -*- coding: utf-8 -*-

# GTK Worker for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 18, 2011

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
            
            if type(args) == tuple:
                rtn = funct(*args)
            elif args:
                rtn = funct(args)
            else:
                rtn = funct()
            
            if callback:
                self.tcallback(callback, rtn, user_data)

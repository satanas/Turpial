# -*- coding: utf-8 -*-

# Qt Worker for Turpial

import Queue

from PyQt4.QtCore import QThread

class Worker(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.queue = Queue.Queue()
        self.exit_ = False

    #def __del__(self):
    #    self.wait()

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
                if user_data:
                    callback(rtn, user_data)
                else:
                    callback(rtn)



# -*- coding: utf-8 -*-

# Singleton for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 20, 2011

import os
import sys
import logging
import tempfile

from libturpial.common.tools import *

if detect_os() == OS_LINUX:
    import fcntl

class Singleton:
    def __init__(self):
        self.fd = None
        self.log = logging.getLogger('Sys')
        self.filepath = os.path.abspath(os.path.join(tempfile.gettempdir(), 
            'turpial.pid'))
        
        if detect_os() == OS_LINUX:
            self.fd = open(self.filepath, 'w')
            try:
                fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                self.__exit()
        elif detect_os() == OS_WINDOWS:
            try:
                # If file already exists, we try to remove it (in case previous
                # execution was interrupted)
                if os.path.exists(self.filepath):
                    os.unlink(self.filepath)
                self.fd = os.open(self.filepath, os.O_CREAT|os.O_EXCL|os.O_RDWR)
            except OSError, err:
                if err.errno == 13:
                    self.__exit()
    
    def __del__(self):
        if detect_os() == OS_WINDOWS:
            if self.fd:
                os.close(self.fd)
                os.unlink(self.filepath)
    
    def __exit(self):
        self.log.error("Another instance is already running")
        sys.exit(-1)

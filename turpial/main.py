#!/usr/bin/python
# -*- coding: utf-8 -*-

# Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 7, 2011

import sys
import logging

from optparse import OptionParser

from turpial.ui import util
from libturpial.common.tools import *
from libturpial.api.core import Core
from libturpial.config import AppConfig

class Turpial:
    def __init__(self):
        parser = OptionParser()
        parser.add_option('-d', '--debug', dest='debug', action='store_true',
            help='show debug info in shell during execution', default=False)
        parser.add_option('-i', '--interface', dest='interface',
            help='select interface to use. Available: %s' % util.available_interfaces(),
            default='cmd')
        parser.add_option('-c', '--clean', dest='clean', action='store_true',
            help='clean all bytecodes', default=False)
        parser.add_option('--version', dest='version', action='store_true',
            help='show the version of Turpial and exit', default=False)
        
        (options, args) = parser.parse_args()
        
        self.core = Core()
        self.config = AppConfig()
        self.interface = options.interface
        #self.version = self.global_cfg.read('App', 'version')
        self.version = '2.0'
        
        if options.debug or options.clean: 
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('Controller')
        
        if options.clean:
            clean_bytecodes(__file__, self.log)
            sys.exit(0)
            
        if options.version:
            print "Turpial v%s" % self.version
            print "Python v%X" % sys.hexversion
            sys.exit(0)
        
        if options.interface in util.INTERFACES.keys():
            self.ui = util.INTERFACES[options.interface](self.core)
        else:
            print "'%s' is not a valid interface. Availables interfaces are %s" % (
                options.interface, util.available_interfaces())
            sys.exit(-1)
        
        self.log.debug('Starting Turpial v%s' % self.version)
        
        self.ui.show_login()
        try:
            self.ui.main_loop()
        except KeyboardInterrupt:
            self.log.debug('Intercepted Keyboard Interrupt')
            self.ui.main_quit()

if __name__ == '__main__':
    t = Turpial()

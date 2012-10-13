#!/usr/bin/python
# -*- coding: utf-8 -*-

# Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 7, 2011

import os
import sys
import logging
import subprocess

from optparse import OptionParser, SUPPRESS_HELP

from turpial import DESC
from turpial.ui import util

from libturpial.api.core import Core
from libturpial.common.tools import *
from libturpial.config import AppConfig
from libturpial import VERSION as LIBTURPIAL_VERSION

LOG_FMT = logging.Formatter('[%(asctime)s] [%(name)s::%(levelname)s] %(message)s', '%Y%m%d-%H:%M')


class Turpial:
    def __init__(self):
        parser = OptParser()
        parser.add_option('-d', '--debug', dest='debug', action='store_true',
            help='show debug info in shell during execution', default=False)
        parser.add_option('-i', '--interface', dest='interface',
            help='select interface to use. Available: %s' % util.available_interfaces(),
            default=util.DEFAULT_INTERFACE)
        parser.add_option('-c', '--clean', dest='clean', action='store_true',
            help='clean all bytecodes', default=False)
        parser.add_option('--version', dest='version', action='store_true',
            help='show the version of Turpial and exit', default=False)
        parser.add_option('-s', dest='mac', action='store_true', default=False,
            help=SUPPRESS_HELP)
        parser.add_option('-p', dest='mac', action='store_true', default=False,
            help=SUPPRESS_HELP)


        (options, args) = parser.parse_args()

        if not options.mac and parser.failed:
            parser.print_help()
            sys.exit(-2)

        self.interface = options.interface

        if options.debug or options.clean:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('Controller')
        #handler = logging.StreamHandler()
        #handler.setFormatter(LOG_FMT)
        #self.log.addHandler(handler)

        self.core = Core()

        if options.clean:
            clean_bytecodes(__file__, self.log)
            sys.exit(0)

        # TODO: Override with any configurated value
        if options.interface in util.INTERFACES.keys():
            self.ui = util.INTERFACES[options.interface](self.core)
        else:
            print "'%s' is not a valid interface. Availables interfaces are %s" % (
            options.interface, util.available_interfaces())
            sys.exit(-1)

        if options.version:
            print DESC
            print "libturpial v%s" % LIBTURPIAL_VERSION
            print "Python v%X" % sys.hexversion
            sys.exit(0)


        self.log.debug('Starting %s' % DESC)

        self.ui.show_main()
        try:
            self.ui.main_loop()
        except KeyboardInterrupt:
            self.log.debug('Intercepted Keyboard Interrupt')
            self.ui.main_quit()

class OptParser(OptionParser):
    def __init__(self):
        OptionParser.__init__(self)
        self.failed = False

    def error(self, error):
        print error
        self.failed = True

    def exit(self):
        pass

def main():
    try:
        subprocess.call(['turpial-unity-daemon', 'stop'])
        subprocess.call(['turpial-unity-daemon', 'start'])
    except:
        pass
    t = Turpial()
    try:
        subprocess.call(['turpial-unity-daemon', 'stop'])
    except:
        pass

if __name__ == '__main__':
    main()

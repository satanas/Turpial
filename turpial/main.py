#!/usr/bin/python
# -*- coding: utf-8 -*-

# Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 7, 2011
import time #quitar, solo aprendiendo pyinstaller

import sys
import logging

from optparse import OptionParser

class OptParser(OptionParser):
    def __init__(self):
        OptionParser.__init__(self)
    def error(self, error):
        pass


from turpial import VERSION
from turpial.ui import util
from libturpial import VERSION as LIBVERSION
from libturpial.common.tools import *
from libturpial.api.core import Core
from libturpial.config import AppConfig

from PyQt4.Qt import *
from PyQt4.QtGui import *
from PyQt4.QtCore import *

import sys
import os

class Test(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        btn = QPushButton("hi")
        layout = QHBoxLayout()
        layout.addWidget(btn)
        self.setLayout(layout)
        btn.clicked.connect(self._p)
        self._printDirs()

    def _p(self):
        print "Hi!"

    def _printDirs(self):
        print "DIRS"
        print "QCoreApplication.applicationDirPath()", QCoreApplication.applicationDirPath()
        print "os.getcwd()", os.getcwd()
        print "os.path.dirname(sys.executable)", os.path.dirname(sys.executable)
        print "sys.path", sys.path
        print "sys.frozen", hasattr(sys, "frozen")
        print "os.curdir", os.curdir

if __name__ == "__mmain__":
    print "start"
    app = QApplication(sys.argv)
    test = Test()
    test.show()
    test.raise_()
    app.exec_()
    print "end"
    app.quit()


class Turpial:
    def __init__(self):
        print str(sys.argv)
        import ssl
        #time.sleep(2)
        print ssl.OPENSSL_VERSION
        #parser = OptionParser()
        parser = OptParser()
        parser.add_option('-d', '--debug', dest='debug', action='store_true',
            help='show debug info in shell during execution', default=False)
        parser.add_option('-i', '--interface', dest='interface',
            help='select interface to use. Available: %s' % util.available_interfaces(),
            default='qt')
        parser.add_option('-c', '--clean', dest='clean', action='store_true',
            help='clean all bytecodes', default=False)
        parser.add_option('--version', dest='version', action='store_true',
            help='show the version of Turpial and exit', default=False)
        parser.add_option('-p','--problem', dest='problem', action='store_true',
            help='give you an important problem to solve', default=False)


        (options, args) = parser.parse_args()
        print "optiones",options
        print "args",args

        self.core = Core()
        self.interface = options.interface
        self.version = "Turpial v%s with libturpial v%s" % (VERSION, LIBVERSION)

        if options.debug or options.clean:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('Controller')

        if options.clean:
            clean_bytecodes(__file__, self.log)
            sys.exit(0)

        if options.version:
            print self.version
            print "Python v%X" % sys.hexversion
            sys.exit(0)

        if options.interface in util.INTERFACES.keys():
            print "asignando valor a self.ui, ",options.interface
            self.ui = util.INTERFACES[options.interface](self.core)
        else:
            print "'%s' is not a valid interface. Availables interfaces are %s" % (
            options.interface, util.available_interfaces())
            sys.exit(-1)

        self.log.debug('Starting %s' % self.version)

        print "show_main() principal"
        self.ui.show_main()
        try:
            print "main_loop() principal"
            self.ui.main_loop()
        except KeyboardInterrupt:
            self.log.debug('Intercepted Keyboard Interrupt')
            print "main_quit() principal"
            self.ui.main_quit()

if __name__ == '__main__':
    t = Turpial()

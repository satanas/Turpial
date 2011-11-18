# -*- coding: utf-8 -*-

# PyQT account form view for Turpial
#
# Author:  Carlos Guerrero (aka guerrerocarlos)
# Started: Sep 11, 2011

import os

import logging
from PyQt4 import QtCore, QtGui
from PyQt4.QtWebKit import *

from turpial.ui.lang import i18n
from turpial.ui.html import HtmlParser
from turpial.ui.qt.htmlview import HtmlView

log = logging.getLogger('PyQt4')

class AccountForm(QtGui.QDialog):
    def __init__(self, parent, plist, user=None, pwd=None, protocol=None):
        super(AccountForm,self).__init__()
        
        self.accwin = parent
        self.htmlparser = HtmlParser(None)
        self.setWindowTitle('Create Account')
        self.resize(290, 200)
        self.finished.connect(self.__close)
        
        self.container = HtmlView()
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)
        
        page = self.htmlparser.account_form(plist)
        self.container.setHtml(page)
        self.show()
        self.working = False
        
    def __close(self, widget, event=None):
        if not self.working:
            self.destroy()
            return False
        else:
            return True
    
    def __action_request(self, widget, url):
        action = url.split(':')[0]
        try:
            args = url.split(':')[1].split('-%&%-')
        except IndexError:
            args = []
        
        if action == "close":
            self.__close(widget)
        elif action == "save_account":
            self.working = True
            self.accwin.save_account(args[0], args[1], args[2])
    
    def cancel_login(self, message):
        self.container.execute("cancel_login('" + msg + "');")
    
    def done_login(self):
        self.destroy()

# -*- coding: utf-8 -*-

# GTK account manager for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2011

import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtWebKit import *
import sys
import Queue
import logging
import threading

from turpial.ui.lang import i18n
from turpial.ui.html import HtmlParser
from turpial.ui.qt.htmlview import HtmlView
#from turpial.ui.gtk.oauthwin import OAuthWindow
#from turpial.ui.qt.account_form import AccountForm

log = logging.getLogger('Gtk')

class Accounts(QtGui.QDialog):
    def __init__(self, parent):
        super(Accounts,self).__init__()
        
        # Main tools
        self.mainwin = parent
        self.core = parent.core
        self.worker = parent.worker
        
        self.htmlparser = HtmlParser(None)
        self.setWindowTitle("Account Manager")
        self.resize(410,350)
        self.finished.connect(self.__close)
        
        self.container = HtmlView(self)
        self.container.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.container.page().linkClicked.connect(self.__action_request)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        self.showed = False
        self.form = None
        self.acc_id = None
        
    def show_all(self, accounts):
        if self.showed:
            self.present()
        else:
            self.showed = True
            page = self.htmlparser.accounts(accounts)
            self.container.setHtml(page)
            self.show()
    
    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True
    
    def __action_request(self, url):
        url = url.toString()
        action = url.split(':')[1]
        try:
            args = url.split(':')[1].split('-%&%-')
        except IndexError:
            args = []
        
        if action == "close":
            self.__close(widget)
        elif action == "new_account":
            self.form = AccountForm(self, self.core.list_protocols())
        elif action == "delete_account":
            self.delete_account(args[0])
        
    def __login_callback(self, arg):
        print 'resp', arg, arg.code, arg.errmsg, arg.items
        
        if arg.code > 0:
            #msg = i18n.get(rtn.errmsg)
            msg = arg.errmsg
            self.form.cancel_login(msg)
            return
        
        auth_obj = arg.items
        if auth_obj.must_auth():
            oauthwin = OAuthWindow(self)
            oauthwin.connect('response', self.__oauth_callback)
            oauthwin.connect('cancel', self.__cancel_callback)
            oauthwin.open(auth_obj.url)
    
    def __cancel_callback(self):
        pass
        
    def __oauth_callback(self, verifier):
        self.worker.register(self.core.authorize_oauth_token, (self.acc_id, verifier), self.__auth_callback)  
    
    def __auth_callback(self):
        self.worker.register(self.core.auth, (self.acc_id), self.__done_callback)
        
    def __done_callback(self, arg):
        if arg.code > 0:
            msg = arg.errmsg
            self.form.cancel_login(msg)
        else:
            self.form.done_login()
            page = self.htmlparser.render_account_list(self.core.all_accounts())
            self.container.update_element("list", page)
        
    def delete_account(self, account_id):
        self.core.unregister_account(account_id, True)
        page = self.htmlparser.render_account_list(self.core.all_accounts())
        self.container.update_element("list", page)
        
    def save_account(self, username, protocol_id, password):
        self.acc_id = self.core.register_account(username, protocol_id, password, True)
        self.worker.register(self.core.login, (self.acc_id), self.__login_callback)

# -*- coding: utf-8 -*-

# GTK account manager for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2011

import os
import gtk
import sys
import Queue
import logging
import threading

from turpial.ui.lang import i18n
from turpial.ui.html import HtmlParser
from turpial.ui.gtk.htmlview import HtmlView
from turpial.ui.gtk.oauthwin import OAuthWindow
from turpial.ui.gtk.account_form import AccountForm

log = logging.getLogger('Gtk')

class Accounts(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        # Main tools
        self.mainwin = parent
        self.core = parent.core
        self.worker = parent.worker
        
        self.htmlparser = HtmlParser(None)
        self.set_title('Account Manager')
        self.set_size_request(310, 350)
        self.set_resizable(False)
        self.set_icon(self.mainwin.load_image('turpial.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        
        self.container = HtmlView()
        self.container.connect('action-request', self.__action_request)
        self.add(self.container)
        self.showed = False
        self.form = None
        self.acc_id = None
        
    def show(self, accounts):
        if self.showed:
            self.present()
        else:
            self.showed = True
            page = self.htmlparser.accounts(accounts)
            self.container.render(page)
            self.show_all()
    
    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True
    
    def __action_request(self, widget, url):
        action = url.split(':')[0]
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

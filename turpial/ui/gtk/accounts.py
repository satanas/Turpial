# -*- coding: utf-8 -*-

# GTK account manager for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2011

import gtk
import logging

from turpial.ui.lang import i18n
from turpial.ui.html import HtmlParser
from turpial.ui.gtk.htmlview import HtmlView
from turpial.ui.gtk.account_form import AccountForm

log = logging.getLogger('Gtk')

class Accounts(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.mainwin = parent
        self.core = self.mainwin.core
        self.htmlparser = HtmlParser()
        self.set_title(i18n.get('accounts'))
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
            self.form = AccountForm(self.mainwin, self, self.core.list_protocols())
        elif action == "delete_account":
            self.mainwin.delete_account(args[0])
    
    def update(self):
        if self.showed:
            page = self.htmlparser.accounts(self.core.all_accounts())
            self.container.render(page)
    
    def cancel_login(self, message):
        if self.form:
            self.form.cancel(message)
            return True
        return False
    
    def done_login(self):
        if self.form:
            self.form.done()
            return True
        return False
    
    def show(self):
        if self.showed:
            self.present()
        else:
            self.showed = True
            self.update()
            self.show_all()
    
    def quit(self):
        self.destroy()
    

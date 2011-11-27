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

log = logging.getLogger('Gtk')

class AccountsDialog(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.mainwin = parent
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
            self.form = AccountForm(self.mainwin, self)
        elif action == "delete_account":
            self.mainwin.delete_account(args[0])
        elif action == "columns":
            #self.__close(widget)
            self.mainwin.columnsdlg.show()
    
    def update(self):
        if self.showed:
            page = self.htmlparser.accounts(self.mainwin.get_all_accounts())
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

class AccountForm(gtk.Window):
    def __init__(self, mainwin, parent, user=None, pwd=None, protocol=None):
        gtk.Window.__init__(self)
        
        self.mainwin = mainwin
        self.set_transient_for(parent)
        self.set_modal(True)
        self.htmlparser = HtmlParser()
        self.set_title(i18n.get('create_account'))
        self.set_size_request(290, 200)
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        
        self.container = HtmlView()
        self.container.connect('action-request', self.__action_request)
        self.add(self.container)
        
        page = self.htmlparser.account_form(self.mainwin.get_protocols_list())
        self.container.render(page)
        self.show_all()
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
            self.mainwin.save_account(args[0], args[1], args[2])
    
    def cancel(self, message):
        self.working = False
        self.container.execute("cancel_login('" + message + "');")
    
    def set_loading_message(self, message):
        pass
        #self.container.execute("set_loading_message('" + message + "');")
        
    def done(self):
        self.working = False
        self.destroy()


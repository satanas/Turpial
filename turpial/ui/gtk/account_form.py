# -*- coding: utf-8 -*-

# GTK account form for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 16, 2011

import os
import gtk
import logging

from turpial.ui.lang import i18n
from turpial.ui.html import HtmlParser
from turpial.ui.gtk.htmlview import HtmlView

log = logging.getLogger('Gtk')

class AccountForm(gtk.Window):
    def __init__(self, parent, plist, user=None, pwd=None, protocol=None):
        gtk.Window.__init__(self)
        
        self.accwin = parent
        self.set_transient_for(parent)
        self.set_modal(True)
        self.htmlparser = HtmlParser(None)
        self.set_title(i18n.get('create_account'))
        self.set_size_request(290, 200)
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        
        self.container = HtmlView()
        self.container.connect('action-request', self.__action_request)
        self.add(self.container)
        
        page = self.htmlparser.account_form(plist)
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
        print url
        print action, args
        if action == "close":
            self.__close(widget)
        elif action == "save_account":
            self.working = True
            self.accwin.save_account(args[0], args[1], args[2])
    
    def cancel_login(self, message):
        self.working = False
        self.container.execute("cancel_login('" + message + "');")
    
    def set_loading_message(self, message):
        pass
        #self.container.execute("set_loading_message('" + message + "');")
        
    def done_login(self):
        self.working = False
        self.destroy()

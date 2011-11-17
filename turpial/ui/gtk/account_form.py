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
        
        self.mainwin = parent
        self.set_transient_for(parent)
        self.set_modal(True)
        self.htmlparser = HtmlParser(None)
        self.set_title('Create Account')
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
    
    def __close(self, widget, event=None):
        self.destroy()
    
    def __action_request(self, widget, url):
        action = url.split(':')[0]
        try:
            args = url.split(':')[1].split('-%&%-')
        except IndexError:
            args = []
        print url
        
        if action == "close":
            self.__close(widget)

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

log = logging.getLogger('Gtk')

class AccountManager(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        self.mainwin = parent
        self.htmlparser = HtmlParser(None)
        self.set_title('Account Manager')
        self.set_size_request(400, 350)
        #self.set_default_size(352, 482)
        self.set_icon(self.mainwin.load_image('turpial.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        #self.connect('key-press-event', self.__on_key_press)
        #self.connect('focus-in-event', self.__on_focus)
        
        self.container = HtmlView()
        self.container.connect('action-request', self.__action_request)
        #self.container.connect('link-request', self.__link_request)
        self.add(self.container)
        
        page = self.htmlparser.accounts()
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
        print action, args

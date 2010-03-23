# -*- coding: utf-8 -*-

"""Widget para realizar la autenticación segura de Twitter desde Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Mar 16, 2010

import gtk
import time
import webkit
import gobject

gobject.threads_init()

class OAuthWindow(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.mainwin = parent
        self.set_title(_('Secure Authentication'))
        self.set_default_size(800, 450)
        self.set_transient_for(parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.connect('delete-event', self.quit)
        
        self.settings = webkit.WebSettings()
        self.view = webkit.WebView()
        self.view.set_settings(self.settings)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.view)
        
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0)
        #self.label.set_line_wrap(True)
        self.label.set_markup(_('Autorize Turpial and copy the given number \
(<b>PIN</b>) in the text box below:'))
        #self.label.set_justify(gtk.JUSTIFY_FILL)
        
        lblbox = gtk.HBox(False, 2)
        lblbox.pack_start(self.label, True, True, 2)
        
        self.pin = gtk.Entry()
        cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        accept = gtk.Button(stock=gtk.STOCK_OK)
        
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(self.pin, True, True, 2)
        hbox.pack_start(cancel, False, False, 2)
        hbox.pack_start(accept, False, False, 2)
        
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(scroll, True, True, 0)
        vbox.pack_start(lblbox, False, False, 2)
        vbox.pack_start(hbox, False, False, 2)
        
        cancel.connect('clicked', self.quit)
        accept.connect('clicked', self.__accept)
        
        self.add(vbox)
        
    def __cancel(self, widget):
        self.quit()
        
    def __accept(self, widget):
        verifier = self.pin.get_text()
        if verifier == '': 
            self.mainwin.cancel_login(_('You must write a valid PIN'))
        else:
            self.mainwin.request_auth_token(verifier)
        self.quit(widget, done=True)
        
    def open(self, uri):
        print uri
        self.view.load_string(_('Loading...'), "text/html", "iso-8859-15", "load")
        self.show_all()
        self.view.open(uri)
        
    def quit(self, widget, event=None, done=False):
        if not done: 
            self.view.stop_loading()
            self.mainwin.cancel_login(_('Login cancelled by user'))
        self.hide()
        return True

#a=OAuthWindow(None)
#a.open('http://twitter.com')

# -*- coding: utf-8 -*-

"""Widget para realizar la autenticación segura de Twitter desde Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Mar 16, 2010

import gtk
import time
import webkit

from turpial.ui.gtk.waiting import CairoWaiting

class OAuthWindow(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.mainwin = parent
        self.set_title(_('Secure Authentication')) ###
        self.set_default_size(800, 450)
        self.set_transient_for(parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.connect('delete-event', self.quit)
        
        self.settings = webkit.WebSettings()
        self.settings.enable_java_applet = False
        #self.settings.enable_plugins = False
        self.settings.enable_page_cache = True
        self.settings.enable_offline_web_application_cache = False
        self.settings.enable_html5_local_storage = False
        self.settings.enable_html5_database = False
        self.settings.enable_default_context_menu = False
        self.view = webkit.WebView()
        self.view.set_settings(self.settings)
        self.view.connect('load-started', self.__started)
        self.view.connect('load-finished', self.__finished)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.view)
        
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0)
        self.label.set_markup(_('Autorize Turpial, copy the <b>PIN</b> in the \
text box below and click OK:'))
        
        self.waiting_label = gtk.Label()
        self.waiting_label.set_use_markup(True)
        self.waiting = CairoWaiting(parent)
        waiting_box = gtk.Alignment(xalign=1.0)
        waiting_box.add(self.waiting_label)
        
        lblbox = gtk.HBox(False, 2)
        lblbox.pack_start(self.label, True, True, 2)
        lblbox.pack_start(waiting_box, True, True, 2)
        lblbox.pack_start(self.waiting, False, False, 2)
        
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
        self.view.stop_loading()
        verifier = self.pin.get_text()
        if verifier == '': 
            self.mainwin.cancel_login(_('You must write a valid PIN'))
        else:
            self.mainwin.request_auth_token(verifier)
        self.quit(widget, done=True)
        
    def __started(self, widget, frame):
        self.waiting.start()
        self.waiting_label.set_markup(_('Loading...'))
        
    def __finished(self, widget, frame):
        self.waiting.stop()
        self.waiting_label.set_markup('')
    
    def open(self, uri):
        print uri
        self.show_all()
        self.view.open(uri)
        
    def quit(self, widget, event=None, done=False):
        if not done: 
            self.view.stop_loading()
            self.mainwin.cancel_login(_('Login cancelled by user'))
        self.hide()
        return True

#a=OAuthWindow(None)
#a.open('http://api.twitter.com/oauth/authorize?oauth_token=pwIujr18cmBmZbQd8sftu23qGSQor2pMLfmJfqMiiCE')

# -*- coding: utf-8 -*-

""" Widget to make the OAuth dance from Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Mar 16, 2010

import gtk
import webkit
import gobject

from turpial.ui.lang import i18n
from turpial.ui.gtk.htmlview import HtmlView

class OAuthWindow(gtk.Window, gobject.GObject):
    __gsignals__ = {
        "response": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
        "cancel": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
    }
    
    def __init__(self, parent):
        gobject.GObject.__init__(self)
        gtk.Window.__init__(self)
        
        self.mainwin = parent
        self.set_title(i18n.get('secure_auth'))
        self.set_default_size(800, 450)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.connect('delete-event', self.__cancel)
        
        self.view = HtmlView()
        self.view.connect('load-started', self.__started)
        self.view.connect('load-finished', self.__finished)
        
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0)
        self.label.set_markup('Autorize Turpial, copy the <b>PIN</b> in the \
text box below and click OK:')
        
        self.waiting_label = gtk.Label()
        self.waiting_label.set_use_markup(True)
        #self.waiting = CairoWaiting(parent)
        waiting_box = gtk.Alignment(xalign=1.0)
        waiting_box.add(self.waiting_label)
        
        lblbox = gtk.HBox(False, 2)
        lblbox.pack_start(self.label, True, True, 2)
        lblbox.pack_start(waiting_box, True, True, 2)
        #lblbox.pack_start(self.waiting, False, False, 2)
        
        self.pin = gtk.Entry()
        cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
        accept = gtk.Button(stock=gtk.STOCK_OK)
        
        hbox = gtk.HBox(False, 0)
        hbox.pack_start(self.pin, True, True, 2)
        hbox.pack_start(cancel, False, False, 2)
        hbox.pack_start(accept, False, False, 2)
        
        vbox = gtk.VBox(False, 5)
        #vbox.pack_start(scroll, True, True, 0)
        vbox.pack_start(self.view, True, True, 0)
        vbox.pack_start(lblbox, False, False, 2)
        vbox.pack_start(hbox, False, False, 2)
        
        cancel.connect('clicked', self.__cancel)
        accept.connect('clicked', self.__accept)
        
        self.add(vbox)
        self.show_all()
        
    def __cancel(self, widget, event=None):
        self.quit()
        
    def __accept(self, widget):
        verifier = self.pin.get_text()
        if verifier == '': 
            #self.mainwin.cancel_login('You must write a valid PIN')
            print 'You must write a valid PIN'
            return
        
        #self.mainwin.request_auth_token(verifier)
        self.quit(verifier)
        
    def __started(self, widget):
        #self.waiting.start()
        self.waiting_label.set_markup('Loading...')
        
    def __finished(self, widget):
        #self.waiting.stop()
        self.waiting_label.set_markup('')
    
    def open(self, uri):
        print uri
        self.show_all()
        self.view.load(uri)
        
    def quit(self, response=None):
        self.view.stop()
        if response: 
            self.emit('response', response)
        else:
            self.emit('cancel')
        self.destroy()
        #return True
        
gobject.type_register(OAuthWindow)

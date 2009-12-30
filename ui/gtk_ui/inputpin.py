# -*- coding: utf-8 -*-

# Widget para solicitar el pin para la autenticación OAuth del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 30, 2009

import gtk

#from ui import util as util

class InputPin(gtk.Dialog):
    def __init__(self, parent):
        gtk.Dialog.__init__(self, 'Input Pin', parent, 
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        
        self.mainwin = parent
        
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)
        self.label.set_markup('<span size="medium"><b>Introduce el PIN:</b></span>')
        self.label.set_justify(gtk.JUSTIFY_LEFT)
        
        self.pin = gtk.Entry()
        
        self.vbox.pack_start(self.label, False, False, 2)
        self.vbox.pack_start(self.pin, True, True, 2)
        self.vbox.show_all()
        

# -*- coding: utf-8 -*-

# Widget para solicitar el pin para la autenticación OAuth del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 30, 2009

import gtk

class InputPin(gtk.Dialog):
    def __init__(self, parent):
        gtk.Dialog.__init__(self, _('Turpial Authorization'), parent,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        
        self.mainwin = parent
        self.set_size_request(380, 220)
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)
        self.label.set_line_wrap(True)
        self.label.set_markup('<span size="medium">%s.\n\n%s\n\n <b>%s:</b>\
</span>' % (_('Twitter has implemented a new security system and needs that \
you authorize Turpial from your account'),
            _('In order to complete that step, Turpial has open \
a new page in your default browser, go there to authorize Turpial and copy \
the number given in the box below...'),
            _('Input PIN'),
            ))
        self.label.set_justify(gtk.JUSTIFY_FILL)
        
        self.pin = gtk.Entry()
        
        self.vbox.pack_start(self.label, False, False, 2)
        self.vbox.pack_start(self.pin, True, True, 2)
        self.vbox.show_all()
        

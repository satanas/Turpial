# -*- coding: utf-8 -*-

# Widget para solicitar el pin para la autenticación OAuth del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 30, 2009

import gtk

class InputPin(gtk.Dialog):
    def __init__(self, parent):
        gtk.Dialog.__init__(self, 'Autorizacion de Turpial', parent, 
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
            'Basic Auth', gtk.RESPONSE_APPLY))
        
        self.mainwin = parent
        self.set_size_request(380, 220)
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)
        self.label.set_line_wrap(True)
        self.label.set_markup('<span size="medium">Twitter ha implementado un nuevo \
sistema de seguridad que implica la autorización de Turpial desde tu cuenta. \
\n\nPara eso, Turpial acaba de abrir una nueva página en el navegador predeterminado, \
desde allí deberás autorizar a Turpial y copiar el número devuelto en la caja \
de texto a continuación...\n\n <b>Introduce el PIN:</b></span>')
        self.label.set_justify(gtk.JUSTIFY_FILL)
        
        self.pin = gtk.Entry()
        
        self.vbox.pack_start(self.label, False, False, 2)
        self.vbox.pack_start(self.pin, True, True, 2)
        self.vbox.show_all()
        

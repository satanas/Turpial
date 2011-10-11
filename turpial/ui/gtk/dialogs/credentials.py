# -*- coding: utf-8 -*-

# Credentials dialog for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 11, 2011

import gtk

from turpial.ui.lang import i18n

class CredentialsDialog(gtk.Dialog):
    def __init__(self, parent, acc_id):
        title = i18n.get('credentials')
        gtk.Dialog.__init__(self, title, parent, 
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
            gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        
        self.set_has_separator(True)
        
        user = '<b>%s</b>' % acc_id.split('-')[0]
        protocol = '<b>%s</b>' %  acc_id.split('-')[1].capitalize()
        text = i18n.get('please_type_password') % (user, protocol)
        
        message_box = gtk.Label()
        message_box.set_use_markup(True)
        message_box.set_alignment(0, 0.5)
        message_box.set_markup(text)
        
        label = gtk.Label()
        label.set_use_markup(True)
        label.set_alignment(0, 0.5)
        label.set_markup(i18n.get('password'))
        
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        
        passwd_box = gtk.HBox(False)
        passwd_box.pack_start(label, False, False)
        passwd_box.pack_start(self.password, True, True, 5)
        
        self.remember = gtk.CheckButton(i18n.get('remember_my_credentials'))
        
        content = gtk.VBox(False)
        content.pack_start(message_box, True, True, 10)
        content.pack_start(passwd_box, False, False, 6)
        content.pack_start(self.remember, False, False)
        
        icon = parent.load_image('dialog-secret.png')
        
        hbox = gtk.HBox(False)
        hbox.pack_start(icon, False, False)
        hbox.pack_start(content, True, True, 10)
        
        self.vbox.pack_start(hbox, True, True)
        self.show_all()

# -*- coding: utf-8 -*-

# Diálogo para seguir amigos
#
# Author: Wil Alvarez (aka Satanas)
# Jul 07, 2010

import gtk

class Follow(gtk.Window):
    def __init__(self, mainwin, friend=''):
        gtk.Window.__init__(self)
        
        self.mainwin = mainwin
        self.set_title(_('Follow'))
        self.set_size_request(260, 80)
        self.set_transient_for(mainwin)
        self.set_resizable(False)
        self.set_modal(True)
        self.set_border_width(6)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        lbl_user = gtk.Label(_('User'))
        self.user = gtk.Entry()
        
        self.btn_ok = gtk.Button(_('Ok'))
        self.btn_ok.set_flags(gtk.CAN_DEFAULT)
        btn_cancel = gtk.Button(_('Cancel'))
        
        hbox = gtk.HBox(False, 6)
        hbox.pack_start(lbl_user, False, False)
        hbox.pack_start(self.user, True, True)
        
        box_button = gtk.HButtonBox()
        box_button.set_spacing(6)
        box_button.set_layout(gtk.BUTTONBOX_END)
        box_button.pack_start(self.btn_ok)
        box_button.pack_start(btn_cancel)
        
        vbox = gtk.VBox(True)
        vbox.pack_start(hbox, False, False)
        vbox.pack_start(box_button, False, False)
        
        self.btn_ok.connect('clicked', self.__follow)
        btn_cancel.connect('clicked', self.__close)
        self.user.connect('activate', self.__follow)
        self.connect('delete-event', self.__close)
        
        self.add(vbox)
        self.show_all()
        self.btn_ok.grab_default()
        self.set_default(self.btn_ok)
        self.user.set_text(friend)
        self.user.select_region(0, -1)
        
    def __close(self, widget, event=None):
        self.destroy()
    
    def __follow(self, widget):
        user = self.user.get_text()
        if user != '':
            self.mainwin.request_follow(user)
        self.__close(widget)
        

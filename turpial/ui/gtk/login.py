# -*- coding: utf-8 -*-

# Widget que representa la ventana de login para Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 08, 2010

import gtk
import base64

from turpial.ui.gtk.loginlabel import LoginLabel
from turpial.ui.gtk.waiting import CairoWaiting
from turpial.config import PROTOCOLS

class LoginBox(gtk.VBox):
    def __init__(self, mainwin):
        gtk.VBox.__init__(self, False, 5)
        
        self.mainwin = mainwin
        avatar = self.mainwin.load_image('logo2.png')
        self.message = LoginLabel(self)
        us, pw, rem = self.mainwin.request_remembered(0)
        
        lbl_user = gtk.Label()
        lbl_user.set_use_markup(True)
        lbl_user.set_markup(u'<span size="small">%s</span>' % _('User and Password'))
        lbl_user.set_alignment(0, 0.5)
        
        self.username = gtk.Entry()
        self.username.set_text(us)
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        self.password.set_text(pw)
        
        self.remember = gtk.CheckButton(_('Remember my credentials'))
        
        self.btn_oauth = gtk.Button(_('Connect'))
        
        list = gtk.ListStore(gtk.gdk.Pixbuf, str, str)
        for p in PROTOCOLS:
            image = '%s.png' % p
            t_icon = self.mainwin.load_image(image, True)
            list.append([t_icon, p, p])
        
        self.combo_protocol = gtk.ComboBox(list)
        icon_cell = gtk.CellRendererPixbuf()
        txt_cell = gtk.CellRendererText()
        self.combo_protocol.pack_start(icon_cell,False)
        self.combo_protocol.pack_start(txt_cell,False)
        self.combo_protocol.add_attribute(icon_cell,'pixbuf',0)
        self.combo_protocol.add_attribute(txt_cell,'markup',1)
        self.combo_protocol.set_active(0)
        
        self.btn_settings = gtk.Button()
        self.btn_settings.set_relief(gtk.RELIEF_NONE)
        self.btn_settings.set_tooltip_text(_('Preferences'))
        self.btn_settings.set_image(self.mainwin.load_image('dock-settings.png'))
        settings_box = gtk.Alignment(xalign=1.0, yalign=0.5)
        settings_box.set_padding(70, 10, 40, 40)
        settings_box.add(self.btn_settings)
        
        self.waiting = CairoWaiting(self.mainwin)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        hbox = gtk.HBox(False)
        hbox.pack_start(lbl_user, False, False, 2)
        hbox.pack_start(align, True, True, 2)
        
        table = gtk.Table(11, 1, False)
        table.attach(avatar, 0, 1, 0, 1, gtk.FILL, gtk.FILL, 10, 50)
        table.attach(self.message, 0, 1, 1, 2, gtk.EXPAND | gtk.FILL, gtk.FILL, 20, 3)
        table.attach(hbox, 0, 1, 2, 3, gtk.EXPAND | gtk.FILL, gtk.FILL, 50, 0)
        table.attach(self.username, 0, 1, 3, 4, gtk.EXPAND | gtk.FILL, gtk.FILL, 50, 0)
        table.attach(self.password, 0, 1, 5, 6, gtk.EXPAND | gtk.FILL, gtk.FILL, 50, 0)
        table.attach(self.combo_protocol, 0, 1, 7, 8, gtk.EXPAND, gtk.FILL, 0, 10)
        table.attach(self.btn_oauth, 0, 1, 8, 9, gtk.EXPAND, gtk.FILL, 0, 3)
        table.attach(self.remember, 0, 1, 9, 10, gtk.EXPAND, gtk.FILL, 0, 3)
        table.attach(settings_box, 0, 1, 10, 11, gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL, 0, 10)
        
        self.pack_start(table, False, False, 2)
        
        self.btn_oauth.connect('clicked', self.signin)
        self.password.connect('activate', self.signin)
        self.rhandler = self.remember.connect("toggled", self.__toogle_remember)
        self.btn_settings.connect('clicked', self.mainwin.show_preferences, 'global')
        self.combo_protocol.connect('changed', self.__change_protocol)
        self.remember.set_active(rem)
        
    def __toogle_remember(self, widget):
        user = self.username.get_text()
        pwd = self.password.get_text()
        rem = self.remember.get_active()
        prot = self.combo_protocol.get_active()
        
        if user == '' or pwd == '':
            self.remember.disconnect(self.rhandler)
            self.remember.set_active(False)
            self.rhandler = self.remember.connect("toggled", 
                self.__toogle_remember)
            self.cancel_login(_('Fields can\'t be empty'))
            return
        
        if rem:
            self.username.set_sensitive(False)
            self.password.set_sensitive(False)
        else:
            self.username.set_sensitive(True)
            self.password.set_sensitive(True)
        
        self.mainwin.request_remember(user, pwd, prot, rem)
            
    def __change_protocol(self, widget):
        prot = self.combo_protocol.get_active()
        us, pw, rem = self.mainwin.request_remembered(prot)
        
        self.username.set_text(us)
        self.password.set_text(pw)
        self.remember.disconnect(self.rhandler)
        self.remember.set_active(rem)
        self.rhandler = self.remember.connect("toggled", self.__toogle_remember)
        
        if rem:
            self.username.set_sensitive(False)
            self.password.set_sensitive(False)
        else:
            self.username.set_sensitive(True)
            self.password.set_sensitive(True)
        
    def signin(self, widget):
        self.message.deactivate()
        self.waiting.start()
        self.btn_oauth.set_sensitive(False)
        self.username.set_sensitive(False)
        self.password.set_sensitive(False)
        self.remember.set_sensitive(False)
        self.btn_settings.set_sensitive(False)
        self.combo_protocol.set_sensitive(False)
        
        prot = self.combo_protocol.get_active()
        self.mainwin.request_signin(self.username.get_text(), 
            self.password.get_text(), PROTOCOLS[prot])
        
    def cancel_login(self, error):
        self.message.set_error(error)
        self.waiting.stop(error=True)
        self.btn_oauth.set_sensitive(True)
        self.remember.set_sensitive(True)
        self.btn_settings.set_sensitive(True)
        self.combo_protocol.set_sensitive(True)
        if not self.remember.get_active():
            self.username.set_sensitive(True)
            self.password.set_sensitive(True)
            

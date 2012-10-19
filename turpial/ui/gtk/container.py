# -*- coding: utf-8 -*-

# GTK3 container for all columns in Turpial

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n

class Container(Gtk.VBox):
    def __init__(self, base):
        Gtk.VBox.__init__(self)

        self.base = base
        self.child = None

    def empty_columns(self):
        if self.child:
            self.remove(self.child)

        placeholder = Gtk.Image()

        image = Gtk.Image()
        image.set_from_pixbuf(self.base.load_image('logo.png', True))

        welcome = Gtk.Label()
        welcome.set_use_markup(True)
        welcome.set_markup('<b>' + i18n.get('welcome') + '</b>')

        no_accounts = Gtk.Label()
        no_accounts.set_use_markup(True)
        no_accounts.set_line_wrap(True)
        no_accounts.set_justify(Gtk.Justification.CENTER)
        no_accounts.set_markup(i18n.get('no_active_accounts'))

        self.child = Gtk.VBox()
        self.child.pack_start(placeholder, False, False, 40)
        self.child.pack_start(image, False, False, 20)
        self.child.pack_start(welcome, False, False, 10)
        self.child.pack_start(no_accounts, False, False, 0)

        self.add(self.child)
        self.show_all()

    def render_columns(self, accounts, columns):
        pass

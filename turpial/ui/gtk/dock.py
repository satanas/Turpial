# -*- coding: utf-8 -*-

# GTK3 dock for Turpial
#
# Author: Wil Alvarez (aka Satanas)

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n

class Dock(Gtk.EventBox):
    def __init__(self, base):
        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 0))

        self.btn_updates = DockButton(base, 'dock-update.png', i18n.get('update_status'))
        self.btn_messages = DockButton(base, 'dock-message.png', i18n.get('direct_messages'))
        self.btn_columns = DockButton(base, 'dock-add.png', i18n.get('columns'))
        self.btn_profiles = DockButton(base, 'dock-profile.png', i18n.get('profiles'))
        self.btn_accounts = DockButton(base, 'dock-accounts.png', i18n.get('accounts'))
        self.btn_preferences = DockButton(base, 'dock-preferences.png', i18n.get('preferences'))
        self.btn_about = DockButton(base, 'dock-about.png', i18n.get('about'))

        self.btn_accounts.connect('clicked', base.show_accounts_dialog)
        self.btn_preferences.connect('clicked', base.show_preferences_dialog)
        self.btn_about.connect('clicked', base.show_about_dialog)

        box = Gtk.HBox()
        box.pack_end(self.btn_updates, False, False, 0)
        box.pack_end(self.btn_messages, False, False, 0)
        box.pack_end(self.btn_columns, False, False, 0)
        box.pack_end(self.btn_profiles, False, False, 0)
        box.pack_end(self.btn_accounts, False, False, 0)
        box.pack_end(self.btn_preferences, False, False, 0)
        box.pack_end(self.btn_about, False, False, 0)

        align = Gtk.Alignment()
        align.set(1, -1, -1, -1)
        align.add(box)

        self.add(align)

    def empty_menu(self):
        self.btn_updates.hide()
        self.btn_profiles.hide()
        self.btn_messages.hide()

    def render_menu(self):
        self.btn_updates.show()
        self.btn_profiles.show()
        self.btn_messages.show()

class DockButton(Gtk.Button):
    def __init__(self, base, image, tooltip):
        Gtk.Button.__init__(self)
        self.set_image(base.load_image(image))
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_tooltip_text(tooltip)

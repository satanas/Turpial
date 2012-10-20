# -*- coding: utf-8 -*-

# GTK3 tray icon for Turpial

from gi.repository import Gtk

from turpial import DESC
from turpial.ui.lang import i18n

class TrayIcon(Gtk.StatusIcon):
    def __init__(self, base):
        Gtk.StatusIcon.__init__(self)

        self.base = base
        self.set_from_pixbuf(self.base.load_image('turpial-tray.png', True))
        self.set_tooltip_text(DESC)
        self.menu = Gtk.Menu()

    def __build_common_menu(self):
        accounts = Gtk.MenuItem(i18n.get('accounts'))
        preferences = Gtk.MenuItem(i18n.get('preferences'))
        sounds = Gtk.CheckMenuItem(i18n.get('enable_sounds'))
        #sound_.set_active(not self.sound._disable)
        exit_ = Gtk.MenuItem(i18n.get('exit'))

        self.menu.append(accounts)
        self.menu.append(preferences)
        self.menu.append(sounds)
        self.menu.append(Gtk.SeparatorMenuItem())
        self.menu.append(exit_)

        accounts.connect('activate', self.base.show_accounts_dialog)
        preferences.connect('activate', self.base.show_preferences_dialog)
        sounds.connect('toggled', self.base.disable_sound)
        exit_.connect('activate', self.base.main_quit)

    def empty(self):
        self.menu = Gtk.Menu()
        self.__build_common_menu()

    def normal(self):
        self.menu = Gtk.Menu()

        tweet = Gtk.MenuItem(i18n.get('new_tweet'))
        tweet.connect('activate', self.base.show_update_box)
        direct = Gtk.MenuItem(i18n.get('direct_message'))
        direct.connect('activate', self.base.show_update_box_for_direct)

        self.menu.append(tweet)
        self.menu.append(direct)

        self.__build_common_menu()

    def popup(self, button, activate_time):
        self.menu.show_all()
        self.menu.popup(None, None, None, None, button, activate_time)
        return True


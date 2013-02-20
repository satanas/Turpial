# -*- coding: utf-8 -*-

# Qt tray icon for Turpial

from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QSystemTrayIcon

from turpial import DESC
from turpial.ui.lang import i18n

class TrayIcon(QSystemTrayIcon):
    def __init__(self, base):
        QSystemTrayIcon.__init__(self)

        self.base = base
        icon = QIcon(base.get_image_path('turpial-tray.png'))
        self.setIcon(icon)
        self.setToolTip(DESC)
        self.show()
        #self.menu = Gtk.Menu()

    def __build_common_menu(self):
        accounts = self.menu.addAction(i18n.get('accounts'))
        preferences = self.menu.addAction(i18n.get('preferences'))
        sounds = self.menu.addAction(i18n.get('enable_sounds'))
        #sound_.set_active(not self.sound._disable)
        self.menu.addSeparator()
        exit_ = self.menu.addAction(i18n.get('exit'), self.base.main_quit)

        #self.menu.append(accounts)
        #self.menu.append(preferences)
        #self.menu.append(sounds)
        #self.menu.append(Gtk.SeparatorMenuItem())
        #self.menu.append(exit_)

        #accounts.connect('activate', self.base.show_accounts_dialog)
        #preferences.connect('activate', self.base.show_preferences_dialog)
        #sounds.connect('toggled', self.base.disable_sound)
        #exit_.connect('activate', self.base.main_quit)

    def empty(self):
        self.menu = QMenu()
        self.__build_common_menu()
        self.setContextMenu(self.menu)

    def normal(self):
        self.menu = QMenu()

        tweet = self.menu.addAction(i18n.get('new_tweet'))
        #tweet.connect('activate', self.base.show_update_box)
        direct = self.menu.addAction(i18n.get('direct_message'))
        #direct.connect('activate', self.base.show_update_box, True)

        self.__build_common_menu()

        self.setContextMenu(self.menu)

    # Change the tray icon image to indicate updates
    def notify(self):
        self.set_from_pixbuf(self.base.load_image('turpial-tray-update.png', True))

    # Clear the tray icon image
    def clear(self):
        self.set_from_pixbuf(self.base.load_image('turpial-tray.png', True))

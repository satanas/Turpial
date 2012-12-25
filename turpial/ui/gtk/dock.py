# -*- coding: utf-8 -*-

# GTK3 dock for Turpial

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n

from libturpial.common import ProtocolType

class Dock(Gtk.EventBox):
    def __init__(self, base):
        Gtk.EventBox.__init__(self)

        self.base = base
        self.column_menu = None
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 0))

        self.btn_updates = DockButton(base, 'dock-updates.png', i18n.get('update_status'))
        self.btn_messages = DockButton(base, 'dock-messages.png', i18n.get('direct_messages'))
        self.btn_search = DockButton(base, 'dock-search.png', i18n.get('search'))
        self.btn_stats = DockButton(base, 'dock-stats.png', i18n.get('statistics'))
        self.btn_columns = DockButton(base, 'dock-columns.png', i18n.get('columns'))
        self.btn_accounts = DockButton(base, 'dock-accounts.png', i18n.get('accounts'))
        self.btn_preferences = DockButton(base, 'dock-preferences.png', i18n.get('preferences'))
        self.btn_about = DockButton(base, 'dock-about.png', i18n.get('about'))

        self.btn_updates.connect('clicked', self.base.show_update_box)
        self.btn_messages.connect('clicked', self.base.show_update_box, True)
        self.btn_search.connect('clicked', self.base.show_search_dialog)
        self.btn_columns.connect('clicked', self.show_columns_menu)
        self.btn_accounts.connect('clicked', self.base.show_accounts_dialog)
        self.btn_preferences.connect('clicked', self.base.show_preferences_dialog)
        self.btn_about.connect('clicked', self.base.show_about_dialog)

        box = Gtk.HBox()
        box.pack_end(self.btn_updates, False, False, 0)
        box.pack_end(self.btn_messages, False, False, 0)
        box.pack_end(self.btn_columns, False, False, 0)
        box.pack_end(self.btn_accounts, False, False, 0)
        box.pack_end(self.btn_search, False, False, 0)
        box.pack_end(self.btn_stats, False, False, 0)
        box.pack_end(self.btn_preferences, False, False, 0)
        box.pack_end(self.btn_about, False, False, 0)

        align = Gtk.Alignment()
        align.set(1, -1, -1, -1)
        align.add(box)

        self.add(align)

    def __save_column(self, widget, column_id):
        self.base.save_column(column_id)

    def empty(self):
        self.btn_updates.hide()
        self.btn_messages.hide()
        self.btn_stats.hide()

    def normal(self):
        self.btn_updates.show()
        self.btn_messages.show()
        self.btn_stats.show()

    def show_columns_menu(self, widget):
        self.menu = Gtk.Menu()

        empty = True
        columns = self.base.get_all_columns()
        reg_columns = self.base.get_registered_columns()

        for acc in self.base.get_all_accounts():
            name = "%s (%s)" % (acc.username, i18n.get(acc.protocol_id))
            temp = Gtk.MenuItem(name)
            if acc.logged_in:
                # Build submenu for columns in each account
                temp_menu = Gtk.Menu()
                for key, col in columns[acc.id_].iteritems():
                    item = Gtk.MenuItem(key)
                    if col.id_ != "":
                        item.set_sensitive(False)
                    item.connect('activate', self.__save_column, col.build_id())
                    temp_menu.append(item)
                # Add public timeline
                public_tl = Gtk.MenuItem(i18n.get('public_timeline').lower())
                public_tl.connect('activate', self.__save_column, acc.id_ + '-public')
                temp_menu.append(public_tl)

                temp.set_submenu(temp_menu)

                # Add view profile item
                temp_menu.append(Gtk.SeparatorMenuItem())
                item = Gtk.MenuItem(i18n.get('view_profile'))
                item.connect('activate', self.__save_column, acc.id_)
                temp_menu.append(item)
            else:
                temp.set_sensitive(False)
            self.menu.append(temp)
            empty = False

        if empty:
            empty_menu = Gtk.MenuItem(i18n.get('no_registered_accounts'))
            empty_menu.set_sensitive(False)
            self.menu.append(empty_menu)
        else:
            self.menu.append(Gtk.SeparatorMenuItem())
        self.menu.show_all()
        self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

class DockButton(Gtk.Button):
    def __init__(self, base, image, tooltip):
        Gtk.Button.__init__(self)
        self.set_image(base.load_image(image))
        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_tooltip_text(tooltip)
        self.set_size_request(24, 24)
        #self.btn_updates.set_default_size(24, 24)


# -*- coding: utf-8 -*-

# GTK3 container for all columns in Turpial

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n
from turpial.ui.gtk.column import StatusesColumn

class Container(Gtk.VBox):
    def __init__(self, base):
        Gtk.VBox.__init__(self)

        self.base = base
        self.child = None
        self.columns = {}
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(65535, 65535,65535))

    def __scrolling_right(self):
        if len(self.columns) > 0:
            adjustment = self.child.get_hadjustment()
            max_value = adjustment.get_upper()
            adjustment.set_value(max_value)

    def empty(self):
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
        if len(self.base.get_accounts_list()) > 0:
            no_accounts.set_markup(i18n.get('no_registered_columns'))
        else:
            no_accounts.set_markup(i18n.get('no_active_accounts'))

        self.child = Gtk.VBox()
        self.child.pack_start(placeholder, False, False, 40)
        self.child.pack_start(image, False, False, 20)
        self.child.pack_start(welcome, False, False, 10)
        self.child.pack_start(no_accounts, False, False, 0)

        self.add(self.child)
        self.show_all()

    def normal(self, accounts, columns):
        self.columns = {}

        box = Gtk.HBox()

        for col in columns:
            self.columns[col.id_] = StatusesColumn(self.base, col)
            box.pack_start(self.columns[col.id_], True, True, 0)

        self.child = Gtk.ScrolledWindow()
        self.child.add_with_viewport(box)

        self.add(self.child)
        self.show_all()

    def start_updating(self, column_id):
        return self.columns[column_id].start_updating()

    def stop_updating(self, column_id, errmsg=None, errtype=None):
        self.columns[column_id].stop_updating()
        if errmsg:
            self.base.show_notice(errmsg, errtype)

    def is_updating(self, column_id):
        return self.columns[column_id].updating

    def update_column(self, column_id, statuses):
        self.columns[column_id].update(statuses)
        self.stop_updating(column_id)

    def add_column(self, column):
        if len(self.columns) > 1:
            self.columns[column.id_] = StatusesColumn(self.base, column)
            hbox = self.child.get_children()[0].get_child()
            hbox.pack_start(self.columns[column.id_], True, True, 0)
        else:
            self.remove(self.child)
            accounts = self.base.get_accounts_list()
            columns = self.base.get_registered_columns()
            self.normal(accounts, columns)

        self.show_all()
        self.scroll()

    def remove_column(self, column_id):
        hbox = self.child.get_children()[0].get_child()
        hbox.remove(self.columns[column_id])
        del self.columns[column_id]
        if len(self.columns) == 0:
            self.empty()

    def exist_column(self, column_id):
        return self.columns.has_key(column_id)

    def mark_status_favorite(self, status):
        # TODO: Optimize this function. Map?
        for key, column in self.columns.iteritems():
            column.mark_favorite(status)

    def unmark_status_favorite(self, status):
        for key, column in self.columns.iteritems():
            column.unmark_favorite(status)

    def mark_status_repeat(self, status):
        for key, column in self.columns.iteritems():
            column.mark_repeat(status)

    def unmark_status_repeat(self, status):
        for key, column in self.columns.iteritems():
            column.unmark_repeat(status)

    def delete_status(self, status):
        for key, column in self.columns.iteritems():
            column.delete_status(status)

    def scroll(self):
        GObject.timeout_add(250, self.__scrolling_right)


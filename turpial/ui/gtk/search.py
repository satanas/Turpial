# -*- coding: utf-8 -*-

# GTK search for Turpial
#
# Author: Wil Alvarez (aka Satanas)

import urllib2
import logging

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n
from turpial.ui.gtk.markuplabel import MarkupLabel

from libturpial.common import ColumnType
from libturpial.common import LoginStatus

log = logging.getLogger('Gtk')

class SearchDialog(Gtk.Window):
    def __init__(self, base):
        Gtk.Window.__init__(self)

        self.base = base
        self.set_title(i18n.get('search'))
        self.set_size_request(300, 120)
        self.set_resizable(False)
        self.set_icon(self.base.load_image('turpial.png', True))
        self.set_transient_for(base)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_gravity(Gdk.Gravity.STATIC)
        self.set_modal(True)
        self.connect('delete-event', self.__close)

        alabel = Gtk.Label(i18n.get('account'))
        clabel = Gtk.Label(i18n.get('criteria'))

        alist = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        for acc in self.base.get_accounts_list():
            image = '%s.png' % acc.split('-')[1]
            icon = self.base.load_image(image, True)
            alist.append([icon, acc.split('-')[0], acc])

        self.account = Gtk.ComboBox()
        self.account.set_model(alist)
        icon = Gtk.CellRendererPixbuf()
        txt = Gtk.CellRendererText()
        self.account.pack_start(icon, False)
        self.account.pack_start(txt, False)
        self.account.add_attribute(icon, 'pixbuf', 0)
        self.account.add_attribute(txt, 'markup', 1)
        self.account.connect('changed', self.__reset_error)

        self.criteria = Gtk.Entry()
        self.criteria.connect('activate', self.__on_add)
        self.criteria.set_tooltip_text(i18n.get('search_criteria_tooltip'))
        self.criteria.connect('changed', self.__reset_error)

        help_text = i18n.get('this_search_support_advanced_operators')
        help_text += ' "", OR, -, from, to, filter, source, place, since, until. '
        help_text += i18n.get('for_more_information_visit')
        help_text += " <a href='https://dev.twitter.com/docs/using-search'>%s</a>" % (
            i18n.get('twitter_search_documentation'))

        help_label = MarkupLabel()
        help_label.set_markup(help_text)
        help_label.set_margin_top(10)
        help_label.set_size_request(300, -1)

        self.error_message = MarkupLabel(xalign=0.5)

        table = Gtk.Table(3, 2, False)
        table.attach(alabel, 0, 1, 0, 1, Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        table.attach(self.account, 1, 2, 0, 1, Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        table.attach(clabel, 0, 1, 1, 2, Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        table.attach(self.criteria, 1, 2, 1, 2, Gtk.AttachOptions.EXPAND|Gtk.AttachOptions.FILL)
        table.attach(help_label, 0, 2, 2, 3, Gtk.AttachOptions.SHRINK)
        table.set_margin_top(4)
        table.set_row_spacing(0, 2)
        table.set_row_spacing(1, 2)

        self.btn_add = Gtk.Button(i18n.get('add'))
        self.btn_close = Gtk.Button(i18n.get('close'))

        self.btn_add.connect('clicked', self.__on_add)
        self.btn_close.connect('clicked', self.__close)

        box_button = Gtk.HButtonBox()
        box_button.set_spacing(6)
        box_button.set_layout(Gtk.ButtonBoxStyle.END)
        box_button.pack_start(self.btn_close, False, False, 0)
        box_button.pack_start(self.btn_add, False, False, 0)
        box_button.set_margin_top(10)

        vbox = Gtk.VBox(False)
        vbox.set_border_width(6)
        vbox.pack_start(table, False, False, 0)
        vbox.pack_start(self.error_message, False, False, 5)
        vbox.pack_start(box_button, False, False, 0)
        self.add(vbox)

    def __close(self, widget, event=None):
        self.destroy()
        return True

    def __reset_error(self, widget=None):
        self.error_message.set_markup('')

    def __on_add(self, widget, event=None):
        model = self.account.get_model()
        index = self.account.get_active()
        criteria = self.criteria.get_text()
        if index < 0 or criteria == '':
            self.error_message.set_error_text(i18n.get('fields_cant_be_empty'))
            self.error_message.set_size_request(-1, 10)
        else:
            account_id = model[index][2]
            column_id = "%s-%s:%s" % (account_id, ColumnType.SEARCH, urllib2.quote(criteria))
            self.base.save_column(column_id)
            self.__close(None)

    def show(self):
        self.show_all()

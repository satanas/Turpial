# -*- coding: utf-8 -*-

# GTK3 widget to implement columns in Turpial

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n
from turpial.ui.gtk.statuswidget import StatusWidget


ICON_MARGIN = 5

class StatusesColumn(Gtk.VBox):
    def __init__(self, base, column):
        Gtk.VBox.__init__(self)

        self.base = base
        self.set_size_request(250, -1)

        # Variables that defines column status
        self.last_id = None
        self.updating = False

        # Header
        #============================================================

        img = '%s.png' % column.protocol_id
        caption = "%s :: %s" % (column.account_id.split('-')[0], column.column_name)
        icon = Gtk.Image()
        icon.set_from_pixbuf(self.base.load_image(img, True))
        icon.set_margin_top(ICON_MARGIN)
        icon.set_margin_right(ICON_MARGIN * 2)
        icon.set_margin_bottom(ICON_MARGIN)
        icon.set_margin_left(ICON_MARGIN)

        label = Gtk.Label()
        label.set_use_markup(True)
        label.set_justify(Gtk.Justification.LEFT)
        label.set_markup('<span foreground="#ffffff"><b>%s</b></span>' % (caption))
        label.set_alignment(0, 0.5)

        btn_close = Gtk.Button()
        btn_close.set_image(self.base.load_image('action-delete.png'))
        btn_close.set_relief(Gtk.ReliefStyle.NONE)
        btn_close.set_tooltip_text(i18n.get('delete_column'))
        btn_close.connect('clicked', self.__delete_column, column.id_)

        self.btn_refresh = Gtk.Button()
        self.btn_refresh.set_image(self.base.load_image('action-refresh.png'))
        self.btn_refresh.set_relief(Gtk.ReliefStyle.NONE)
        self.btn_refresh.set_tooltip_text(i18n.get('manual_update'))

        self.spinner = Gtk.Spinner()

        inner_header = Gtk.HBox()
        inner_header.pack_start(icon, False, False, 0)
        inner_header.pack_start(label, True, True, 0)
        inner_header.pack_start(btn_close, False, False, 0)
        inner_header.pack_start(self.btn_refresh, False, False, 0)
        inner_header.pack_start(self.spinner, False, False, 0)

        header = Gtk.EventBox()
        header.add(inner_header)
        header.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 0))

        # Content
        #============================================================
        self._list = Gtk.VBox()
        scroll = Gtk.ScrolledWindow()
        scroll.add_with_viewport(self._list)
        scroll.set_margin_top(ICON_MARGIN)
        scroll.set_margin_right(ICON_MARGIN)
        scroll.set_margin_bottom(ICON_MARGIN)
        scroll.set_margin_left(ICON_MARGIN)

        content = Gtk.EventBox()
        content.add(scroll)

        self.pack_start(header, False, False, 0)
        self.pack_start(content, True, True, 0)

    def __delete_column(self, widget, column_id):
        self.base.delete_column(column_id)

    def __add_status(self, status):
        s = StatusWidget(self.base, status)
        self._list.pack_start(s, False, False, 0)

    def __mark_favorite(self, child, status):
        if child.status.id_ != status.id_:
            return
        child.set_favorited_mark(True)

    def __unmark_favorite(self, child, status):
        if child.status.id_ != status.id_:
            return
        child.set_favorited_mark(False)

    def __mark_repeat(self, child, status):
        if child.status.id_ != status.id_:
            return
        child.set_repeated_mark(True)

    def __unmark_repeat(self, child, status):
        if child.status.id_ != status.id_:
            return
        child.set_repeated_mark(False)

    def __delete_status(self, child, status):
        if child.status.id_ != status.id_:
            return
        self._list.remove(child)

    def show(self):
        self.show_all()
        self.spinner.hide()

    def clear(self):
        # TODO: Fix or reimplement
        self.model.clear()

    def start_updating(self):
        self.btn_refresh.hide()
        self.spinner.start()
        self.updating = True
        return self.last_id

    def stop_updating(self):
        self.spinner.stop()
        self.spinner.hide()
        self.btn_refresh.show()
        self.updating = False

    def update(self, statuses):
        for status in statuses:
            self.__add_status(status)
        #self._list.disconnect(self.click_handler)

        #self.mark_all_as_read()
        #self.__set_last_time()

        #new_count = 0
        #if len(self.model) == 0:
        #    self.__add_statuses(statuses)
        #else:
        #    new_count = self.__modify_statuses(statuses)

        #if self.get_vadjustment().get_value() == 0.0:
        #    self.list.scroll_to_cell((0,))

        self.last_id = statuses[0].id_
        #self.click_handler = self.list.connect("cursor-changed", self.__on_select)

    def mark_favorite(self, status):
        self._list.foreach(self.__mark_favorite, status)

    def unmark_favorite(self, status):
        self._list.foreach(self.__unmark_favorite, status)

    def mark_repeat(self, status):
        self._list.foreach(self.__mark_repeat, status)

    def unmark_repeat(self, status):
        self._list.foreach(self.__unmark_repeat, status)

    def delete_status(self, status):
        self._list.foreach(self.__delete_status, status)

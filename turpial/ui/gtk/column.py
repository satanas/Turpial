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
        self.menu = None
        self.column = column

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

        self.btn_config = Gtk.Button()
        self.btn_config.set_image(self.base.load_image('action-refresh.png'))
        self.btn_config.set_relief(Gtk.ReliefStyle.NONE)
        self.btn_config.set_tooltip_text(i18n.get('column_options'))
        self.btn_config.connect('clicked', self.show_config_menu)
        self.connect('realize', self.__on_realize)

        self.spinner = Gtk.Spinner()

        inner_header = Gtk.HBox()
        inner_header.pack_start(icon, False, False, 0)
        inner_header.pack_start(label, True, True, 0)
        inner_header.pack_start(btn_close, False, False, 0)
        inner_header.pack_start(self.btn_config, False, False, 0)
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

        self.show_all()

        self.btn_config.hide()
        self.spinner.show()

    def __delete_column(self, widget, column_id):
        self.base.delete_column(column_id)

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

    def __refresh(self, widget, column_id):
        self.base.refresh_column(column_id)

    def __on_realize(self, widget, data=None):
        # Assuming that this code is only executed the first time you instance
        # a Status Column
        self.btn_config.hide()
        self.spinner.start()
        self.spinner.show()

    def clear(self):
        # TODO: Fix or reimplement
        self.model.clear()

    def start_updating(self):
        self.spinner.start()
        self.spinner.show()
        self.btn_config.hide()
        self.updating = True
        return self.last_id

    def stop_updating(self):
        self.spinner.stop()
        self.spinner.hide()
        self.btn_config.show()
        self.updating = False

    def update(self, statuses):
        children = self._list.get_children()
        empty = not(bool(children))
        to_del = 0
        num_children = len(children)
        num_statuses = len(statuses)
        max_statuses = self.base.get_max_statuses_per_column()
        if not empty:
            if (num_children + num_statuses) >= max_statuses:
                to_del = (num_children + num_statuses) - max_statuses
            else:
                to_del = num_children
            for i in range(to_del):
                self._list.remove(children[-1])
                del(children[-1])

        # Set last_id before reverse, that way we guarantee that last_id holds
        # the id for the newest status
        self.last_id = statuses[0].id_

        statuses.reverse()

        for status in statuses:
            s = StatusWidget(self.base, status)
            self._list.pack_start(s, False, False, 0)
            self._list.reorder_child(s, 0)

        #self.mark_all_as_read()
        #self.__set_last_time()

        #new_count = 0
        #if len(self.model) == 0:
        #    self.__add_statuses(statuses)
        #else:
        #    new_count = self.__modify_statuses(statuses)

        #if self.get_vadjustment().get_value() == 0.0:
        #    self.list.scroll_to_cell((0,))

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

    def show_config_menu(self, widget):
        notif = Gtk.CheckMenuItem(i18n.get('notificate'))
        sound = Gtk.CheckMenuItem(i18n.get('sound'))
        refresh = Gtk.MenuItem(i18n.get('manual_update'))
        refresh.connect('activate', self.__refresh, self.column.id_)

        self.menu = Gtk.Menu()
        self.menu.append(sound)
        self.menu.append(notif)
        self.menu.append(refresh)

        self.menu.show_all()
        self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

# -*- coding: utf-8 -*-

# GTK3 widget to implement columns in Turpial

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n

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

        self.model = Gtk.ListStore(
            str, # id_
            str, # display_id
            str, # in_reply_to_id
            GdkPixbuf.Pixbuf, # avatar
            str, # account_id
            str, # username
            str, # pango_message
            str, # clean_message
            str, # datetime
            str, # reposted_by
            str, # client
            bool, # favorite?
            bool, # verified?
            bool, # protected?
            bool, # own?
            bool, # new?
            str, # status type
            str, # protocol
            int, # timestamp
            Gdk.Color, # color
        )

        self.model.append([
            '1','1','1',
            None,
            '1','username','hola mundo','hola mundo','123','123','123',
            False,False,False,False,False,
            'asd','asd',0,None])
        self.model.set_sort_column_id(18, Gtk.SortType.DESCENDING)

        avatar = Gtk.CellRendererPixbuf()
        avatar.set_property('yalign', 0)

        status = Gtk.CellRendererText()
        status.set_property('wrap-mode', Pango.WrapMode.WORD_CHAR)
        status.set_property('wrap-width', 260)
        status.set_property('yalign', 0)
        status.set_property('xalign', 0)

        column = Gtk.TreeViewColumn('statuss')
        column.set_alignment(0.0)
        column.pack_start(avatar, False)
        column.pack_start(status, True)
        column.add_attribute(status, 'markup', 6)
        column.add_attribute(status, 'cell_background_gdk', 19)
        column.add_attribute(avatar, 'pixbuf', 3)
        column.add_attribute(avatar, 'cell_background_gdk', 19)

        self._list = Gtk.TreeView()
        self._list.set_headers_visible(False)
        self._list.set_level_indentation(0)
        self._list.set_resize_mode(Gtk.ResizeMode.IMMEDIATE)
        self._list.set_model(self.model)
        self._list.append_column(column)
        #self._list.connect("button-release-event", self.__on_click)
        #self.click_handler = self._list.connect("cursor-changed", self.__on_select)

        scroll = Gtk.ScrolledWindow()
        scroll.add(self._list)
        scroll.set_margin_top(ICON_MARGIN)
        scroll.set_margin_right(ICON_MARGIN)
        scroll.set_margin_bottom(ICON_MARGIN)
        scroll.set_margin_left(ICON_MARGIN)

        content = Gtk.EventBox()
        content.add(scroll)

        self.pack_start(header, False, False, 0)
        self.pack_start(content, True, True, 0)

    def show(self):
        self.show_all()
        self.spinner.hide()

    def clear(self):
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
        self._list.disconnect(self.click_handler)
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

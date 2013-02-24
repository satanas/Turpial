# -*- coding: utf-8 -*-

# GTK3 widget to implement columns in Turpial

import urllib2

from xml.sax.saxutils import unescape

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import GdkPixbuf
from gi.repository import PangoCairo

from turpial.ui.lang import i18n
from libturpial.common import StatusType


ICON_MARGIN = 5

class StatusesColumn(Gtk.VBox):
    def __init__(self, base, column):
        Gtk.VBox.__init__(self)

        self.base = base
        self.set_size_request(250, -1)
        #self.set_double_buffered(True)

        # Variables that defines column status
        self.last_id = None
        self.updating = False
        self.menu = None
        self.column = column

        # Header
        #============================================================

        img = '%s.png' % column.protocol_id
        caption = "%s :: %s" % (column.account_id.split('-')[0],
            urllib2.unquote(column.column_name))
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

        self._list = Gtk.TreeView()
        self._list.set_headers_visible(False)
        #self._list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self._list.set_level_indentation(0)
        #self._list.set_resize_mode(gtk.RESIZE_IMMEDIATE)

        self.model = Gtk.ListStore(
            GdkPixbuf.Pixbuf, # avatar
            str, # id
            str, # username
            str, # plain text message
            str, # datetime
            str, # client
            bool, # favorited?
            bool, # repeated?
            bool, # own?
            bool, # protected?
            bool, # verified?
            str, # in_reply_to_id
            str, # in_reply_to_user
            str, # reposted_by
            Gdk.Color, # color
            int, # status type
            str, # account_id
            float, # unix timestamp
        )

        # Sort by unix timestamp
        self.model.set_sort_column_id(17, Gtk.SortType.DESCENDING)

        cell_avatar = Gtk.CellRendererPixbuf()
        cell_avatar.set_property('yalign', 0)
        cell_status = StatusCellRenderer(self.base, self._list)
        cell_status.set_property('wrap-mode', Pango.WrapMode.WORD_CHAR)
        cell_status.set_property('wrap-width', 260)
        cell_status.set_property('yalign', 0)
        cell_status.set_property('xalign', 0)

        column = Gtk.TreeViewColumn('tweets')
        column.set_alignment(0.0)
        column.pack_start(cell_avatar, False)
        column.pack_start(cell_status, True)
        column.set_attributes(cell_status, text=3, datetime=4, client=5,
            favorited=6, repeated=7, protected=9, verified=10, username=2,
            reposted_by=13, cell_background_gdk=14)
        column.set_attributes(cell_avatar, pixbuf=0, cell_background_gdk=14)


        self._list.set_model(self.model)
        self._list.append_column(column)
        #self._list.connect("button-release-event", self.__on_click)
        #self.click_handler = self._list.connect("cursor-changed", self.__on_select)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
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

    def __build_pango_text(self, status):
        ''' Transform the regular text into pango markup '''
        return status.text
        pango_twt = unescape(status.text)
        pango_twt = pango_twt.replace('&quot;', '"')
        pango_twt = pango_twt.replace('\r\n', ' ')
        pango_twt = pango_twt.replace('\n', ' ')

        print pango_twt

        pango_twt = GObject.markup_escape_text(pango_twt)

        user = '<span size="9000" foreground="%s"><b>%s</b></span>\n' % (
            self.base.get_color_scheme('links'), status.username
        )
        pango_twt = '<span size="9000">%s</span>' % pango_twt
        #pango_twt = self.__highlight_hashtags(pango_twt)
        #pango_twt = self.__highlight_groups(pango_twt)
        #pango_twt = self.__highlight_mentions(pango_twt)
        #pango_twt = self.__highlight_urls(urls, pango_twt)
        pango_twt += '<span size="2000">\n\n</span>'

        try:
            pango_twt = user + pango_twt
        except UnicodeDecodeError:
            clear_txt = ''
            invalid_chars = []
            for c in pango_twt:
                try:
                    clear_txt += c.encode('ascii')
                except UnicodeDecodeError:
                    invalid_chars.append(c)
                    clear_txt += '?'
            log.debug('Problema con caracteres inválidos en un tweet: %s' % invalid_chars)
            pango_twt = clear_txt

        footer = '<span size="small" foreground="#999">%s' % status.datetime
        #if status.source:
        #    footer += ' %s %s' % (i18n.get('from'), status.source.name)
        if status.in_reply_to_user:
            footer += ' %s %s' % (i18n.get('in_reply_to'), status.in_reply_to_user)
        if status.reposted_by:
            footer += '\n%s %s' % (i18n.get('retweeted_by'), status.reposted_by)
        footer += '</span>'
        pango_twt += footer

        return pango_twt


    def clear(self):
        self._list.get_model().clear()

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
        to_del = 0
        num_children = len(self._list)
        num_statuses = len(statuses)
        max_statuses = self.base.get_max_statuses_per_column()

        if num_children > 0:
            if (num_children + num_statuses) >= max_statuses:
                to_del = (num_children + num_statuses) - max_statuses
            else:
                to_del = num_statuses

            for i in range(to_del):
                last = self._list.iter_n_children(None)
                _iter = self._list.get_iter_from_string(str(last - 1))
                print '    Deleting: %s' % self._list.get_value(_iter, 15)[:30]
                self._list.remove(_iter)

        self.clear()
        # Set last_id before reverse, that way we guarantee that last_id holds
        # the id for the newest status
        self.last_id = statuses[0].id_

        statuses.reverse()

        for status in statuses:
            # This is to avoid insert duplicated statuses
            #if status.id_ in [c.status.id_ for c in children]:
            #    print 'Duplicated status. Nothing to do'
            #    continue

            print '    Adding: %s' % status.text
            pix = self.base.load_image('unknown.png', True)
            pango_text = self.__build_pango_text(status)

            row = [pix, str(status.id_), status.username, pango_text, status.datetime, status.source.name,
                status.favorited, status.repeated, status.is_own, status.protected, status.verified,
                str(status.in_reply_to_id), status.in_reply_to_user, status.reposted_by, None,
                StatusType.NORMAL, status.account_id, status.timestamp]
            self._list.get_model().append(row)

        print '    %i statuses after update' % len(self._list.get_children())

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

    ###def mark_favorite(self, status):
    ###    self._list.foreach(self.__mark_favorite, status)

    ###def unmark_favorite(self, status):
    ###    self._list.foreach(self.__unmark_favorite, status)

    ###def mark_repeat(self, status):
    ###    self._list.foreach(self.__mark_repeat, status)

    ###def unmark_repeat(self, status):
    ###    self._list.foreach(self.__unmark_repeat, status)

    ###def delete_status(self, status):
    ###    self._list.foreach(self.__delete_status, status)

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


class StatusCellRenderer(Gtk.CellRendererText):
    username = GObject.property(type=str, default='')
    datetime = GObject.property(type=str, default='')
    client = GObject.property(type=str, default='')
    favorited = GObject.property(type=bool, default=False)
    repeated = GObject.property(type=bool, default=False)
    protected = GObject.property(type=bool, default=False)
    verified = GObject.property(type=bool, default=False)
    reposted_by = GObject.property(type=str, default='')

    HEADER_PADDING = MESSAGE_PADDING = 4

    def __init__(self, base, treeview):
        GObject.GObject.__init__(self)
        self.base = base
        #self._layout = treeview.create_pango_layout('')

        # With this, we accumulate the width of each part of header
        self.accum_header_width = 0
        # This holds the total height for a given status
        self.total_height = 0


    def __render_reposted_icon(self, cr, cell_area):
        if not self.get_property('reposted_by'):
            self.accum_header_width += self.HEADER_PADDING
            return

        y = cell_area.y
        x = cell_area.x + self.HEADER_PADDING
        icon = self.base.load_image('mark-reposted.png', True)
        Gdk.cairo_set_source_pixbuf(cr, icon, x, y)
        self.accum_header_width += icon.get_width() + self.HEADER_PADDING
        cr.paint()
        del icon
        return

    def __render_username(self, text, context, cr, cell_area, layout):
        y = cell_area.y
        x = cell_area.x + self.accum_header_width

        user = '<span size="9000" foreground="%s"><b>%s</b></span>' % (
            self.base.get_color_scheme('links'), unicode(text))
        layout.set_markup(user, -1)
        inkRect, logicalRect = layout.get_pixel_extents()
        self.accum_header_width += logicalRect.width + self.HEADER_PADDING
        self.total_height = 20

        context.save()
        Gtk.render_layout(context, cr, x, y, layout)
        context.restore()
        return

    def __render_protected_icon(self, cr, cell_area):
        if not self.get_property('protected'):
            return

        y = cell_area.y
        x = cell_area.x + self.accum_header_width
        icon = self.base.load_image('mark-protected.png', True)
        Gdk.cairo_set_source_pixbuf(cr, icon, x, y)
        self.accum_header_width += icon.get_width() + self.HEADER_PADDING
        cr.paint()
        del icon
        return

    def __render_verified_icon(self, cr, cell_area):
        if not self.get_property('verified'):
            return

        y = cell_area.y
        x = cell_area.x + self.accum_header_width
        icon = self.base.load_image('mark-verified.png', True)
        Gdk.cairo_set_source_pixbuf(cr, icon, x, y)
        # TODO: Do it with cairo_context.move_to
        self.accum_header_width += icon.get_width() + self.HEADER_PADDING
        cr.paint()
        del icon
        return

    def __render_message(self, text, context, cr, cell_area, layout):
        y = cell_area.y + self.total_height
        x = cell_area.x + self.MESSAGE_PADDING

        text = unicode(self.get_property('text'))
        print type(text), text
        text = u''.join([text]).decode('utf-8')
        print type(text)
        #escaped_text = GObject.markup_escape_text(text.decode('utf-8'))
        #print escaped_text
        pango_text = u'<span size="9000">%s</span>' % text

        layout.set_markup(pango_text, -1)

        inkRect, logicalRect = layout.get_pixel_extents()
        self.total_height += logicalRect.height + self.MESSAGE_PADDING

        context.save()
        Gtk.render_layout(context, cr, x, y, layout)
        context.restore()
        return

    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    def do_get_preferred_height_for_width(self, treeview, width):
        print width, self.total_height
        return self.total_height, width

    def do_render(self, cr, widget, bg_area, cell_area, flags):
        # Initialize values
        self.accum_header_width = 0
        self.total_height = 0

        context = widget.get_style_context()
        xpad = self.get_property('xpad')
        ypad = self.get_property('ypad')

        # Setting up font and layout
        font = Pango.FontDescription('Sans')
        layout = PangoCairo.create_layout(cr)
        layout.set_wrap(Pango.WrapMode.WORD)
        layout.set_font_description(font)
        layout.set_width(Pango.SCALE * cell_area.width)
        username = self.get_property('username')
        text = self.get_property('text')

        print username, 'protected', self.get_property('protected'), 'verified', self.get_property('verified')

        context.save()

        # Render header
        self.__render_reposted_icon(cr, cell_area)
        self.__render_username(username, context, cr, cell_area, layout)
        self.__render_protected_icon(cr, cell_area)
        self.__render_verified_icon(cr, cell_area)

        self.__render_message(text, context, cr, cell_area, layout)

        context.restore()
        return

# -*- coding: utf-8 -*-

# GTK3 widget to implement statuses in Turpial

import re

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n
from turpial.ui.gtk.common import *
from turpial.ui.gtk.statusmenu import StatusMenu
#from turpial.ui.gtk.imagebutton import ImageButton
from turpial.ui.gtk.markuplabel import MarkupLabel


class StatusWidget(Gtk.EventBox): 
    def __init__(self, base, status):
        Gtk.EventBox.__init__(self)

        self.base = base
        self.status = status
        self.set_margin_bottom(OUTTER_BOTTOM_MARGIN)
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(65535, 65535, 65535))

        # Variables to control work in progress over the status
        self.in_progress = {
            StatusProgress.FAVING:  False,
            StatusProgress.UNFAVING: False,
            StatusProgress.RETWEETING: False,
            StatusProgress.UNRETWEETING: False,
            StatusProgress.DELETING: False,
        }

        self.avatar = Gtk.Image()
        self.avatar.set_margin_right(AVATAR_MARGIN)
        avatar_box = Gtk.Alignment()
        avatar_box.add(self.avatar)
        avatar_box.set(0.5, 0, -1, -1)
        avatar_box.connect('button-press-event', self.__on_click_avatar)

        self.favorited_mark = Gtk.Image()
        self.protected_mark = Gtk.Image()
        self.verified_mark = Gtk.Image()
        self.reposted_mark = Gtk.Image()
        self.repeated_mark = Gtk.Image()

        self.username = MarkupLabel(act_as_link=True)
        self.username.set_ellipsize(Pango.EllipsizeMode.END)
        self.status_text = MarkupLabel()
        self.status_text.connect('activate-link', self.__open_url)
        self.footer = MarkupLabel()

        # Setting user image
        self.avatar.set_from_pixbuf(self.base.load_image('unknown.png', True))
        # Building the status style
        user = '<span size="9000" foreground="%s"><b>%s</b></span>' % (
            self.base.get_color_scheme('links'), status.username
        )
        self.username.set_markup(user)

        text = status.text.replace('&gt;', '>')
        text = text.replace('&lt;', '<')
        pango_text = '<span size="9000">%s</span>' % escape_text_for_markup(text)
        pango_text = self.__highlight_urls(status, pango_text)
        pango_text = self.__highlight_hashtags(status, pango_text)
        pango_text = self.__highlight_groups(status, pango_text)
        pango_text = self.__highlight_mentions(status, pango_text)
        self.status_text.set_markup(pango_text)

        footer = '<span size="small" foreground="#999">%s' % status.datetime
        if status.source:
            footer += ' %s %s' % (_('from'), status.source.name)
        if status.in_reply_to_user:
            footer += ' %s %s' % (_('in reply to'), status.in_reply_to_user)
        if status.reposted_by:
            footer += '\n%s %s' % (_('Retweeted by'), status.reposted_by)
        footer += '</span>'
        self.footer.set_markup(footer)

        starbox = Gtk.HBox()
        starbox.pack_start(self.repeated_mark, False, False, 2)
        starbox.pack_start(self.favorited_mark, False, False, 2)

        staralign = Gtk.Alignment()
        staralign.set(1, -1, -1, -1)
        staralign.add(starbox)

        header = Gtk.HBox()
        header.pack_start(self.reposted_mark, False, False, 2)
        header.pack_start(self.username, False, False, 2)
        header.pack_start(self.verified_mark, False, False, 2)
        header.pack_start(self.protected_mark, False, False, 0)
        header.pack_start(staralign, True, True, 0)

        content = Gtk.VBox()
        content.pack_start(header, False, False, 0)
        content.pack_start(self.status_text, True, True, 0)
        content.pack_start(self.footer, False, False, 0)

        box = Gtk.HBox()
        box.pack_start(avatar_box, False, False, 0)
        box.pack_start(content, True, True, 0)

        bbox = Gtk.VBox()
        bbox.pack_start(box, True, True, 0)
        self.add(bbox)
        self.show_all()

        # After showing all widgets we set the marks
        self.set_favorited_mark(status.favorited)
        self.set_protected_mark(status.protected)
        self.set_verified_mark(status.verified)
        self.set_repeated_mark(status.repeated)
        self.set_reposted_mark(status.reposted_by)

        self.connect('button-release-event', self.__on_click)

        self.base.fetch_status_avatar(status, self.update_avatar)

    def __on_click(self, widget, event=None, data=None):
        # Capture clicks for avatar
        if event.x <= 48 and event.y <= 48 and event.button == 1:
            self.__on_click_avatar()
            return True

        if event.button != 3:
            return False
        self.menu = StatusMenu(self.base, self.status, self.in_progress)
        self.menu.show_all()
        self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    def __on_click_avatar(self):
        self.base.show_user_avatar(self.status.account_id, self.status.username)

    def __highlight_urls(self, status, text):
        for url in status.entities['urls']:
            if url.url == None:
                url.url = url.search_for
            cad = "<a href='%s'>%s</a>" % (escape_text_for_markup(url.url), escape_text_for_markup(url.display_text))
            text = text.replace(url.search_for, cad)
        return text

    def __highlight_hashtags(self, status, text):
        for h in status.entities['hashtags']:
            url = "%s-search:%%23%s" % (self.status.account_id, h.display_text[1:])
            cad = '<a href="hashtags:%s">%s</a>' % (url, h.display_text)
            text = text.replace(h.search_for, cad)
        return text

    def __highlight_groups(self, status, text):
        for h in status.entities['groups']:
            cad = '<a href="groups:%s">%s</a>' % (h.url, h.display_text)
            text = text.replace(h.search_for, cad)
        return text

    def __highlight_mentions(self, status, text):
        for h in status.entities['mentions']:
            args = "%s:%s" % (status.account_id, h.display_text[1:])
            cad = '<a href="profile:%s">%s</a>' % (args, h.display_text)
            pattern = re.compile(h.search_for, re.IGNORECASE)
            text = pattern.sub(cad, text)
        return text

    def __open_url(self, widget, url):
        if url.startswith('http'):
            self.base.open_url(url)
        elif url.startswith('hashtag'):
            column_id = url.replace('hashtags:', '')
            self.base.save_column(column_id)
        elif url.startswith('groups'):
            print "Opening groups"
        elif url.startswith('profile'):
            url = url.replace('profile:', '')
            account_id = url.split(':')[0]
            username = url.split(':')[1]
            self.base.show_user_profile(account_id, username)
        return True

    def update(self, status):
        self.status = status
        # render again

    def update_avatar(self, response):
        if response.code == 0:
            pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(response.items, 48, 48, True)
            self.avatar.set_from_pixbuf(pix)
            del pix

    def set_favorited_mark(self, value):
        if value:
            self.favorited_mark.set_from_pixbuf(self.base.load_image('mark-favorite.png', True))
        else:
            self.favorited_mark.set_from_pixbuf(None)
        self.status.favorited = value

    def set_repeated_mark(self, value):
        if value:
            self.repeated_mark.set_from_pixbuf(self.base.load_image('mark-repeated.png', True))
        else:
            self.repeated_mark.set_from_pixbuf(None)
        self.status.repeated = value

    def set_protected_mark(self, value):
        if value:
            self.protected_mark.set_from_pixbuf(self.base.load_image('mark-protected.png', True))
        else:
            self.protected_mark.set_from_pixbuf(None)

    def set_verified_mark(self, value):
        if value:
            self.verified_mark.set_from_pixbuf(self.base.load_image('mark-verified.png', True))
        else:
            self.verified_mark.set_from_pixbuf(None)

    def set_reposted_mark(self, value):
        if value:
            self.reposted_mark.set_from_pixbuf(self.base.load_image('mark-reposted.png', True))
        else:
            self.reposted_mark.set_from_pixbuf(None)


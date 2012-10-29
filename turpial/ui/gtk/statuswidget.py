# -*- coding: utf-8 -*-

# GTK3 widget to implement statuses in Turpial

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n
from turpial.ui.gtk.markuplabel import MarkupLabel


class StatusWidget(Gtk.VBox):
    OUTTER_BOTTOM_MARGIN = 5
    AVATAR_MARGIN = 5

    def __init__(self, base, status):
        Gtk.VBox.__init__(self)

        self.base = base
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0,0 ))
        self.set_margin_bottom(self.OUTTER_BOTTOM_MARGIN)

        self.avatar = Gtk.Image()
        self.avatar.set_margin_right(self.AVATAR_MARGIN)
        self.favorite_mark = Gtk.Image()
        self.protected_mark = Gtk.Image()
        self.verified_mark = Gtk.Image()
        self.reposted_mark = Gtk.Image()

        self.username = MarkupLabel()
        self.status_text = MarkupLabel()
        self.footer = MarkupLabel()

        # Setting user image
        self.avatar.set_from_pixbuf(self.base.load_image('unknown.png', True))
        # Building the status style
        user = '<span size="9000" foreground="%s"><b>%s</b></span>' % (
            self.base.get_color_scheme('links'), status.username
        )
        self.username.set_markup(user)

        pango_text = '<span size="9000">%s</span>' % status.text
        pango_text = self.__highlight_urls(status, status.text)
        #pango_text = self.__highlight_hashtags(pango_text)
        #pango_text = self.__highlight_groups(pango_text)
        #pango_text = self.__highlight_mentions(pango_text)
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

        header = Gtk.HBox()
        header.pack_start(self.reposted_mark, False, False, 0)
        header.pack_start(self.username, True, True, 0)
        header.pack_start(self.verified_mark, False, False, 0)
        header.pack_start(self.protected_mark, False, False, 0)
        header.pack_start(self.favorite_mark, False, False, 0)

        content = Gtk.VBox()
        content.pack_start(header, False, False, 0)
        content.pack_start(self.status_text, True, True, 0)
        content.pack_start(self.footer, False, False, 0)

        box = Gtk.HBox()
        box.pack_start(self.avatar, False, False, 0)
        box.pack_start(content, True, True, 0)

        self.add(box)
        self.show_all()

    def __highlight_urls(self, status, text):
        for url in status.entities['urls']:
            if url.url == None:
                url.url = url.search_for
            cad = "<a href='%s'>%s</a>" % (url.url, url.display_text)
            print cad
            #if not showmediautils.is_service_supported(url.url):
            #    cad = '<a href="%s" title="%s">%s</a>' % (url.url, url.url,
            #        url.display_text)
            #else:
            #    pars = ARG_SEP.join([url.url.replace(":", "$"), status.account_id])
            #    cad = '<a href="%s" title="%s">%s</a>' % (pars, url.url,
            #        url.display_text)
            text = text.replace(url.search_for, cad)
        return text

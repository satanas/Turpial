# -*- coding: utf-8 -*-

# GTK3 widget to implement status menu in Turpial

from gi.repository import Gtk

from turpial.ui.lang import i18n
from turpial.ui.gtk.common import *

from libturpial.common import StatusType, ProtocolType

class StatusMenu(Gtk.Menu):
    def __init__(self, base, status, in_progress):
        Gtk.Menu.__init__(self)

        self.base = base
        # Detect if current status is performing some operation
        for k,v in in_progress.iteritems():
            if v:
                self.__busy_item(i18n.get(k))
                return

        if status._type == StatusType.NORMAL:
            self.__normal(status)
        elif status._type == StatusType.DIRECT:
            self.__direct_message(status)

    def __busy_item(self, text):
        busymenu = Gtk.MenuItem(text)
        busymenu.set_sensitive(False)
        self.append(busymenu)

    def __reply_item(self, status, direct=False):
        if not status.is_own:
            item = Gtk.MenuItem(i18n.get('reply'))
            if direct:
                pass
            else:
                item.connect('activate', self.__on_reply, status)
            self.append(item)

    def __repeat_item(self, status):
        # TODO: Validates if is protected
        if not status.is_own:
            if status.get_protocol_id() == ProtocolType.TWITTER:
                qt = "RT @%s %s" % (status.username, status.text)
                if status.retweeted:
                    repeat = Gtk.MenuItem(i18n.get('retweeted'))
                    repeat.connect('activate', self.__on_unrepeat, status)
                else:
                    repeat = Gtk.MenuItem(i18n.get('retweet'))
                    repeat.connect('activate', self.__on_repeat, status)
            elif status.get_protocol_id() == ProtocolType.IDENTICA:
                qt = "RD @%s %s" % (status.username, status.text)
                if status.retweeted:
                    repeat = Gtk.MenuItem(i18n.get('redented'))
                    repeat.connect('activate', self.__on_unrepeat, status)
                else:
                    repeat = Gtk.MenuItem(i18n.get('redent'))
                    repeat.connect('activate', self.__on_repeat, status)

            quote = Gtk.MenuItem(i18n.get('quote'))
            quote.connect('activate', self.__on_quote, qt)

            self.append(repeat)
            self.append(quote)

    def __fav_item(self, status):
        if status.favorited:
            unfav = Gtk.MenuItem(i18n.get('favorited'))
            unfav.connect('activate', self.__on_unfavorite, status)
            self.append(unfav)
        else:
            fav = Gtk.MenuItem(i18n.get('favorite'))
            fav.connect('activate', self.__on_favorite, status)
            self.append(fav)


    def __conversation_item(self, status):
        if status.in_reply_to_id:
            in_reply = Gtk.MenuItem(i18n.get('view_conversation'))
            self.append(in_reply)

    def __delete_item(self, status):
        if status.is_own:
            delete = Gtk.MenuItem(i18n.get('delete'))
            delete.connect('activate', self.__on_delete, status)
            self.append(delete)

    def __delete_message_item(self, status):
        if status.is_own:
            delete = Gtk.MenuItem(i18n.get('delete'))
            delete.connect('activate', self.__on_delete_message, status)
            self.append(delete)

    def __delete_direct_message_item(self, status):
        delete = Gtk.MenuItem(i18n.get('delete'))
        self.append(delete)

    # Callbacks

    def __on_reply(self, widget, status):
        self.base.show_update_box_for_reply(status.in_reply_to_id,
                status.account_id, ' '.join(map(lambda x: '@' + x, status.get_reply_mentions())))

    def __on_quote(self, widget, message):
        self.base.show_update_box_for_quote(message)

    def __on_repeat(self, widget, status):
        self.base.confirm_repeat_status(status)

    def __on_unrepeat(self, widget, status):
        self.base.confirm_unrepeat_status(status)

    def __on_favorite(self, widget, status):
        self.base.confirm_favorite_status(status)

    def __on_unfavorite(self, widget, status):
        self.base.confirm_unfavorite_status(status)

    def __on_delete(self, widget, status):
        self.base.confirm_delete_status(status)

    def __on_delete_message(self, widget, status):
        pass

    # Methods to build menu

    def __normal(self, status):
        self.__reply_item(status)
        self.__repeat_item(status)
        self.__delete_item(status)
        self.__fav_item(status)
        self.__conversation_item(status)

    def __direct_message(self, status):
        self.__reply_item(status, True)
        self.__delete_direct_message_item(status)



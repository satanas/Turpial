# -*- coding: utf-8 -*-

# GTK profile dialog for Turpial
#
# Author: Wil Alvarez (aka Satanas)

import logging

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n
from turpial.ui.gtk.common import *
from turpial.ui.gtk.markuplabel import MarkupLabel

log = logging.getLogger('Gtk')

BORDER_WIDTH = 8

class ProfileDialog(Gtk.Window):
    STATUS_IDLE = 0
    STATUS_LOADING = 1
    STATUS_LOADED = 2

    def __init__(self, base):
        Gtk.Window.__init__(self)

        self.base = base
        self.window_width = 300
        self.set_title(i18n.get('user_profile'))
        self.set_default_size(self.window_width, 250)
        #self.set_resizable(False)
        self.set_icon(self.base.load_image('turpial.png', True))
        self.set_transient_for(self.base)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_gravity(Gdk.Gravity.STATIC)
        self.connect('delete-event', self.__close)
        #self.connect('key-press-event', self.__key_pressed)

        self.profile_box = ProfileBox(self.base)

        # Error stuffs
        self.error_msg = Gtk.Label()
        self.error_msg.set_alignment(0.5, 0.5)

        self.spinner = Gtk.Spinner()

        self.loading_box = Gtk.Box(spacing=0)
        self.loading_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.loading_box.pack_start(self.spinner, True, False, 0)
        self.loading_box.pack_start(self.error_msg, True,True, 0)

        self.showed = False

    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True

    def __key_pressed(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Escape':
            self.__close(widget)

    def __clear(self):
        current_child = self.get_child()
        if current_child:
            self.remove(current_child)
        self.status = self.STATUS_IDLE
        self.error_msg.hide()

    def loading(self):
        self.__clear()
        self.spinner.start()
        self.add(self.loading_box)
        self.status = self.STATUS_LOADING
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.show_all()

    def update(self, profile):
        self.__clear()
        self.add(self.profile_box)
        self.profile_box.update(profile)
        self.show_all()

        self.status = self.STATUS_LOADED
        self.present()

    def show(self, profile):
        if self.showed:
            self.present()
        else:
            self.showed = True
            self.show_all()
            self.update(profile)

    def error(self, error=''):
        if error:
            self.error_msg.set_label(error)
        else:
            self.error_msg.set_label(i18n.get('error_loading_profile'))
        self.spinner.stop()
        self.spinner.hide()


    def quit(self):
        self.destroy()

class ProfileBox(Gtk.VBox):
    def __init__(self, base):
        Gtk.VBox.__init__(self, spacing=0)

        self.base = base
        self.avatar = Gtk.Image()
        self.avatar.set_margin_right(AVATAR_MARGIN)
        # This resize is to avoid bad redimentioning on parent window
        self.set_size_request(300, -1)
        avatar_box = Gtk.Alignment()
        avatar_box.add(self.avatar)
        avatar_box.set(0.5, 0, -1, -1)
        #avatar_box.connect('button-press-event', self.__on_click_avatar)

        self.favorited_mark = Gtk.Image()
        self.protected_mark = Gtk.Image()
        self.verified_mark = Gtk.Image()
        self.reposted_mark = Gtk.Image()
        self.repeated_mark = Gtk.Image()

        self.username = MarkupLabel()
        self.username.set_ellipsize(Pango.EllipsizeMode.END)
        self.fullname = MarkupLabel()

        fullname_box = Gtk.HBox()
        fullname_box.pack_start(self.fullname, False, False, 2)
        fullname_box.pack_start(self.verified_mark, False, False, 2)
        fullname_box.pack_start(self.protected_mark, False, False, 0)

        userdata_box = Gtk.VBox()
        userdata_box.pack_start(fullname_box, False, False, 2)
        userdata_box.pack_start(self.username, False, False, 2)

        header_box = Gtk.HBox()
        header_box.set_border_width(BORDER_WIDTH)
        header_box.pack_start(avatar_box, False, False, 0)
        header_box.pack_start(userdata_box, False, False, 0)

        self.bio = DescriptionBox(self.base, 'icon-bio.png', i18n.get('bio'))
        self.location = DescriptionBox(self.base, 'icon-location.png', i18n.get('location'))
        self.web = DescriptionBox(self.base, 'icon-home.png', i18n.get('web'))

        desc_box = Gtk.VBox(spacing=0)
        desc_box.set_border_width(BORDER_WIDTH)
        desc_box.pack_start(self.bio, False, False, 0)
        desc_box.pack_start(self.location, False, False, 0)
        desc_box.pack_start(self.web, False, False, 0)

        self.following = StatBox(i18n.get('following'))
        self.followers = StatBox(i18n.get('followers'))
        self.statuses = StatBox(i18n.get('statuses'))
        self.favorites = StatBox(i18n.get('favorites'))

        stats_box = Gtk.HBox(spacing=0)
        stats_box.set_border_width(BORDER_WIDTH)
        stats_box.pack_start(self.following, True, True, 0)
        stats_box.pack_start(Gtk.VSeparator(), False, False, 2)
        stats_box.pack_start(self.followers, True, True, 0)
        stats_box.pack_start(Gtk.VSeparator(), False, False, 2)
        stats_box.pack_start(self.statuses, True, True, 0)
        stats_box.pack_start(Gtk.VSeparator(), False, False, 2)
        stats_box.pack_start(self.favorites, True, True, 0)

        self.pack_start(header_box, False, False, 0)
        self.pack_start(Gtk.HSeparator(), False, False, 0)
        self.pack_start(desc_box, False, False, 0)
        self.pack_start(Gtk.HSeparator(), False, False, 0)
        self.pack_start(stats_box, False, False, 0)

    def update(self, profile):
        self.base.fetch_status_avatar(profile, self.update_avatar)

        self.avatar.set_from_pixbuf(self.base.load_image('unknown.png', True))
        name = '<span size="9000" foreground="%s"><b>%s</b></span>' % (
            self.base.get_color_scheme('links'), profile.fullname
        )
        self.fullname.set_markup(name)
        self.username.set_markup('@' + profile.username)
        if profile.bio != '':
            self.bio.set_description(profile.bio)
        if profile.location != '':
            self.location.set_description(profile.location)
        if profile.url:
            self.web.set_description(profile.url, True)

        # After showing all widgets we set the marks
        if profile.protected:
            self.set_protected_mark(True)
        else:
            self.set_protected_mark(False)

        if profile.verified:
            self.set_verified_mark(True)
        else:
            self.set_verified_mark(False)

        self.following.set_value(profile.friends_count)
        self.followers.set_value(profile.followers_count)
        self.statuses.set_value(profile.statuses_count)
        self.favorites.set_value(profile.favorites_count)

    def update_avatar(self, response):
        if response.code == 0:
            pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(response.items, 48, 48, True)
            self.avatar.set_from_pixbuf(pix)
            del pix

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

class DescriptionBox(Gtk.VBox):
    def __init__(self, base, image, caption):
        Gtk.VBox.__init__(self, spacing=0)

        icon = Gtk.Image()
        icon.set_from_pixbuf(base.load_image(image, True))
        title = MarkupLabel()
        title.set_markup('<b>%s</b>' % caption)
        self.description = MarkupLabel()
        self.description.set_margin_bottom(10)

        title_box = Gtk.HBox()
        title_box.set_margin_bottom(4)
        title_box.pack_start(icon, False, False, 0)
        title_box.pack_start(title, False, False, 5)

        desc_box = Gtk.HBox()
        desc_box.pack_start(self.description, True, True, 0)

        self.pack_start(title_box, False, False, 0)
        self.pack_start(desc_box, False, False, 0)

    def set_description(self, message, as_link=False):
        if as_link:
            self.description.set_markup('<a href="%s">%s</a>' % (message, message))
        else:
            self.description.set_markup(message)

class StatBox(Gtk.VBox):
    def __init__(self, caption):
        Gtk.VBox.__init__(self, spacing=0)

        self.value = MarkupLabel(xalign=0.5)
        self.value.set_margin_bottom(6)
        self.caption = MarkupLabel(xalign=0.5)
        self.caption.set_text(caption)

        self.pack_start(self.value, False, False, 0)
        self.pack_start(self.caption, False, False, 0)

    def set_value(self, value):
        self.value.set_markup('<b>%s</b>' % value)


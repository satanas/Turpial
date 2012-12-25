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

class ProfileDialog(Gtk.Window):
    STATUS_IDLE = 0
    STATUS_LOADING = 1
    STATUS_LOADED = 2

    def __init__(self, base):
        Gtk.Window.__init__(self)

        self.base = base
        self.window_width = 300
        self.set_title(i18n.get('user_profile'))
        self.set_size_request(self.window_width, 320)
        #self.set_resizable(False)
        self.set_icon(self.base.load_image('turpial.png', True))
        self.set_transient_for(base)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_gravity(Gdk.Gravity.STATIC)
        self.connect('delete-event', self.__close)
        #self.connect('key-press-event', self.__key_pressed)

        self.avatar = Gtk.Image()
        self.avatar.set_margin_right(AVATAR_MARGIN)
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

        header = Gtk.HBox()
        header.pack_start(avatar_box, False, False, 0)
        header.pack_start(userdata_box, False, False, 0)

        bio_icon = Gtk.Image()
        bio_icon.set_from_pixbuf(self.base.load_image('icon-bio.png', True))
        bio_title = MarkupLabel()
        bio_title.set_markup('<b>%s</b>' % i18n.get('bio'))
        self.bio = MarkupLabel()
        #self.bio.set_size_request(self.window_width, -1)
        bio_title_box = Gtk.HBox()
        bio_title_box.pack_start(bio_icon, False, False, 2)
        bio_title_box.pack_start(bio_title, False, False, 2)
        bio_box = Gtk.VBox()
        bio_box.pack_start(bio_title_box, False, False, 0)
        bio_box.pack_start(self.bio, False, False, 0)

        self.profile_box = Gtk.VBox()
        self.profile_box.pack_start(header, False, False, 0)
        self.profile_box.pack_start(bio_box, False, False, 0)

        # Error stuffs
        self.error_msg = Gtk.Label()
        self.error_msg.set_alignment(0.5, 0.5)

        self.spinner = Gtk.Spinner()

        self.loading_box = Gtk.Box(spacing=0)
        self.loading_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.loading_box.pack_start(self.spinner, True, False, 0)
        self.loading_box.pack_start(self.error_msg, True,True, 0)

        #vbox = Gtk.VBox(False)
        #vbox.set_border_width(6)
        #vbox.pack_start(scroll, True, True, 0)
        #vbox.pack_start(box_button, False, False, 6)
        #self.add(vbox)



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
        self.avatar.set_from_pixbuf(self.base.load_image('unknown.png', True))
        name = '<span size="9000" foreground="%s"><b>%s</b></span>' % (
            self.base.get_color_scheme('links'), 'Pedro Perez'
        )
        self.fullname.set_markup(name)
        self.username.set_markup('@pedroperez')
        self.bio.set_markup("Look, just because I don't be givin' no man a foot massage don't make it right for Marsellus to throw Antwone into a glass motherfuckin' house, fuckin' up the way the nigger talks")

        # After showing all widgets we set the marks
        self.set_protected_mark(True)
        self.set_verified_mark(True)

        self.add(self.profile_box)
        self.status = self.STATUS_LOADED
        self.show_all()
        self.set_size_request(self.window_width, 320)
        self.present()

    def show(self, profile):
        if self.showed:
            self.present()
        else:
            self.showed = True
            self.update(profile)
            self.show_all()

    def quit(self):
        self.destroy()

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

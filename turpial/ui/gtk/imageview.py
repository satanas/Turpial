# -*- coding: utf-8 -*-

""" Window to show embedded images """
#
# Author: Wil Alvarez (aka Satanas)
# Aug 31, 2012

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf

from turpial.ui.lang import i18n

class ImageView(Gtk.Window):
    STATUS_IDLE = 0
    STATUS_LOADING = 1
    STATUS_LOADED = 2

    def __init__(self, baseui):
        Gtk.Window.__init__(self)

        self.mainwin = baseui
        self.set_title(i18n.get('image_preview'))
        self.set_size_request(100, 100)
        self.set_default_size(300, 300)
        self.set_transient_for(baseui)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.connect('delete-event', self.quit)
        self.connect('size-allocate', self.__resize)

        self.error_msg = Gtk.Label()
        self.error_msg.set_alignment(0.5, 0.5)

        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(96, 96)

        self.loading_box = Gtk.Box(spacing=0)
        self.loading_box.set_orientation(Gtk.Orientation.VERTICAL)
        self.loading_box.pack_start(self.spinner, True, False, 0)
        self.loading_box.pack_start(self.error_msg, True,True, 0)

        self.image = Gtk.Image()
        self.image_box = Gtk.ScrolledWindow()
        self.image_box.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

        image_box = Gtk.EventBox()
        image_box.add(self.image)
        image_box.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 0))
        self.image_box.add_with_viewport(image_box)

        self.last_size = (0, 0)
        self.status = self.STATUS_IDLE
        self.pixbuf = None

    def __resize(self, widget, allocation=None):
        if self.status != self.STATUS_LOADED:
            return

        if allocation:
            if self.last_size == (allocation.width, allocation.height):
                return
            win_width, win_height = allocation.width, allocation.height
        else:
            win_width, win_height = self.get_size()

        scale = min(float(win_width)/self.pix_width, float(win_height)/self.pix_height)
        new_width = int(scale * self.pix_width)
        new_height = int(scale * self.pix_height)
        pix = self.pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(pix)
        del pix
        self.last_size = self.get_size()

    def __clear(self):
        current_child = self.get_child()
        if current_child:
            self.remove(current_child)

        del self.pixbuf
        self.pixbuf = None
        self.status = self.STATUS_IDLE
        self.error_msg.hide()

    def loading(self):
        self.__clear()
        self.spinner.start()
        self.resize(300, 300)
        self.add(self.loading_box)
        self.status = self.STATUS_LOADING
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.show_all()

    def update(self, path):
        self.__clear()
        self.spinner.stop()
        self.add(self.image_box)

        # Picture information. This will not change until the next update
        self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        self.pix_width = self.pixbuf.get_width()
        self.pix_height = self.pixbuf.get_height()
        self.pix_rate = self.pix_width / self.pix_height

        self.status = self.STATUS_LOADED
        self.resize(self.pix_width, self.pix_height)
        self.show_all()
        self.present()

    def error(self, error=''):
        if error:
            self.error_msg.set_label(error)
        else:
            self.error_msg.set_label(i18n.get('error_loading_image'))
        self.spinner.stop()
        self.spinner.hide()

    def quit(self, widget, event):
        self.hide()
        self.__clear()
        self.last_size = (300, 300)
        return True

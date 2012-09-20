# -*- coding: utf-8 -*-

""" Window to show embedded images """
#
# Author: Wil Alvarez (aka Satanas)
# Aug 31, 2012

import gtk

from turpial.ui.lang import i18n

class ImageView(gtk.Window):
    STATUS_IDLE = 0
    STATUS_LOADING = 1
    STATUS_LOADED = 2

    def __init__(self, baseui):
        gtk.Window.__init__(self)

        self.mainwin = baseui
        self.set_title(i18n.get('image_preview'))
        self.set_size_request(100, 100)
        self.set_default_size(300, 300)
        self.set_transient_for(baseui)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.connect('delete-event', self.quit)
        self.connect('size-allocate', self.__resize)

        self.loading_msg = gtk.Label()
        self.loading_msg.set_alignment(0.5, 0.5)

        self.image = gtk.Image()
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scroll.add(self.image)

        self.box = gtk.EventBox()
        self.box.add(scroll)
        self.box.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color())

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
        pix = self.pixbuf.scale_simple(new_width, new_height, gtk.gdk.INTERP_BILINEAR)
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

    def loading(self):
        self.__clear()
        self.loading_msg.set_label(i18n.get('loading'))
        self.add(self.loading_msg)
        self.status = self.STATUS_LOADING
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.show_all()

    def update(self, url):
        self.__clear()
        self.add(self.box)

        # Picture information. This will not change until the next update
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(url)
        self.pix_width = self.pixbuf.get_width()
        self.pix_height = self.pixbuf.get_height()
        self.pix_rate = self.pix_width / self.pix_height

        self.status = self.STATUS_LOADED
        self.__resize(self)
        self.show_all()
        self.present()

    def error(self, error=''):
        if error:
            self.loading_msg.set_label(error)
        else:
            self.loading_msg.set_label(i18n.get('error_loading_image'))

    def quit(self, widget, event):
        self.hide()
        self.__clear()
        self.last_size = (300, 300)
        return True

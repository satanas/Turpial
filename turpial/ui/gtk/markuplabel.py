# -*- coding: utf-8 -*-

# GTK3 widget to implement labels with markup in Turpial

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango

from turpial.ui.gtk.common import *

class MarkupLabel(Gtk.Label):
    def __init__(self, xalign=0, yalign=0.5, act_as_link=False):
        Gtk.Label.__init__(self)

        self.act_as_link = act_as_link
        self.set_use_markup(True)
        self.set_justify(Gtk.Justification.LEFT)
        self.set_alignment(xalign, yalign)
        self.set_line_wrap(True)
        self.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        #self.set_single_line_mode(False)

        self.connect("size-allocate", self.__on_size_allocate)

    def __on_size_allocate(self, widget, rect):

        print self.get_layout().get_width()
        print self.get_layout().get_height()
        print self.get_layout().is_wrapped()

        self.get_layout().set_width(rect.width)
        #self.set_max_width_chars(
        #self.set_size_request(rect.width, -1)
        #self.set_size_request(-1, -1)

    #def set_markup(self, text):
    #    Gtk.Label.set_markup(self, text)

    def set_error_text(self, text):
        text = escape_text_for_markup(text)
        self.set_markup("<span foreground='#ff0000'>%s</span>" % text) # size='small'

    def set_handy_cursor(self):
        handy_cursor = Gdk.Cursor(Gdk.CursorType.HAND1)
        self.get_window().set_cursor(handy_cursor)

    def show(self):
        Gtk.Label.show(self)
        if self.act_as_link:
            self.set_handy_cursor()

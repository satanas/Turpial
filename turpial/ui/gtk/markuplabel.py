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

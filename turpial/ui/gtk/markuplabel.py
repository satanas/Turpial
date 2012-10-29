# -*- coding: utf-8 -*-

# GTK3 widget to implement labels with markup in Turpial

from gi.repository import Gtk
from gi.repository import Pango


class MarkupLabel(Gtk.Label):
    def __init__(self):
        Gtk.Label.__init__(self)

        self.set_use_markup(True)
        self.set_justify(Gtk.Justification.LEFT)
        self.set_alignment(0, 0.5)
        self.set_line_wrap(True)
        self.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

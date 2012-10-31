# -*- coding: utf-8 -*-

# GTK3 widget to implement labels with markup in Turpial

from gi.repository import Gtk
from gi.repository import Pango

from turpial.ui.gtk.common import *

class MarkupLabel(Gtk.Label):
    def __init__(self, xalign=0, yalign=0.5):
        Gtk.Label.__init__(self)

        self.set_use_markup(True)
        self.set_justify(Gtk.Justification.LEFT)
        self.set_alignment(xalign, yalign)
        self.set_line_wrap(True)
        self.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)

    def set_error_text(self, text):
        text = escape_text_for_markup(text)
        self.set_markup("<span size='small' foreground='#ff0000'>%s</span>" % text)

    def set_markup(self, text):
        Gtk.Label.set_markup(self, text)

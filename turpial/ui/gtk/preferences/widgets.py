# -*- coding: utf-8 -*-

""" Preferences widgets for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)

from gi.repository import Gtk

class GenericTab(Gtk.VBox):
    def __init__(self, desc, current=None):
        Gtk.VBox.__init__(self, False)

        self.current = current
        description = Gtk.Label()
        description.set_line_wrap(True)
        description.set_use_markup(True)
        description.set_markup(desc)
        description.set_justify(Gtk.Justification.FILL)

        desc_align = Gtk.Alignment(xalign=0.0, yalign=0.0)
        desc_align.set_padding(0, 5, 10, 10)
        desc_align.add(description)

        self._container = Gtk.VBox(False, 2)

        hbox = Gtk.HBox(False, 10)
        hbox.pack_start(self._container, True, True, 10)

        self.pack_start(desc_align, False, False, 5)
        self.pack_start(hbox, True, True, 0)

    def add_child(self, child, expand=True, fill=True, padding=0):
        self._container.pack_start(child, expand, fill, padding)

    def get_config(self):
        raise NotImplemented

class TitleLabel(Gtk.Alignment):
    def __init__(self, text, padding=0):
        Gtk.Alignment.__init__(self, xalign=0.0, yalign=0.0)
        caption ="<b>%s</b>" % text
        label = Gtk.Label()
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.set_markup(caption)
        label.set_justify(Gtk.Justification.FILL)

        self.set_padding(10, 0, padding, 0)
        self.add(label)

class CheckBox(Gtk.Alignment):
    def __init__(self, title, is_active, tooltip, padding=0):
        Gtk.Alignment.__init__(self)
        self.set_padding(0, 0, padding, 0)

        self.checkbtn = Gtk.CheckButton(title)
        self.checkbtn.set_active(is_active)
        try:
            self.checkbtn.set_has_tooltip(True)
            self.checkbtn.set_tooltip_text(tooltip)
        except Exception:
            pass
        self.add(self.checkbtn)

    def get_active(self):
        return self.checkbtn.get_active()

class ComboBox(Gtk.HBox):
    def __init__(self, caption, array, current):
        Gtk.HBox.__init__(self, False)
        i = 0
        default = -1
        lbl = Gtk.Label(caption)
        lbl.set_alignment(0.0, 0.5)
        self.combo = Gtk.ComboBoxText()
        self.combo.set_size_request(180, -1)
        for key, v in array.iteritems():
            self.combo.append_text(key)
            if key == current:
                default = i
            i += 1
        self.combo.set_active(default)

        self.pack_start(self.combo, False, False, 5)
        self.pack_start(lbl, True, True, 5)

    def get_active_text(self):
        return self.combo.get_active_text()

class FormField(Gtk.HBox):
    def __init__(self, caption, current, password=False):
        Gtk.HBox.__init__(self, False)
        lbl = Gtk.Label(caption)
        lbl.set_alignment(0.0, 0.5)
        self.entry = Gtk.Entry()
        if password:
            self.entry.set_visibility(False)
        self.entry.set_size_request(180, -1)
        self.entry.set_text(current)

        self.pack_start(self.entry, False, False, 2)
        self.pack_start(lbl, True, True, 5)

    def get_text(self):
        return self.entry.get_text()

class ProxyField(Gtk.HBox):
    def __init__(self, caption, server, port):
        Gtk.HBox.__init__(self, False)
        lbl = Gtk.Label(caption)
        lbl.set_alignment(0.0, 0.5)
        self.server = Gtk.Entry()
        self.server.set_size_request(130, -1)
        self.server.set_text(server)

        self.port = Gtk.Entry()
        self.port.set_size_request(50, -1)
        self.port.set_text(port)

        self.pack_start(self.server, False, False, 2)
        self.pack_start(self.port, False, False, 2)
        self.pack_start(lbl, True, True, 5)

    def get_proxy(self):
        return self.server.get_text(), self.port.get_text()

class HSeparator(Gtk.HBox):
    def __init__(self, spacing=15):
        Gtk.HBox.__init__(self, False)
        self.set_size_request(-1, spacing)

class TimeScroll(Gtk.HBox):
    def __init__(self, caption='', val=5, min=1, max=60, step=3, page=6, size=0, lbl_size=150, unit=''):
        Gtk.HBox.__init__(self, False)

        self.value = val
        self.unit = unit
        self.caption = caption

        self.label = Gtk.Label()
        self.label.set_size_request(lbl_size, -1)
        self.label.set_alignment(xalign=0.0, yalign=0.5)
        self.label.set_use_markup(True)

        adj = Gtk.Adjustment(val, min, max, step, page, size)
        scale = Gtk.HScale()
        scale.set_draw_value(False)
        scale.set_adjustment(adj)
        scale.set_property('value-pos', Gtk.PositionType.RIGHT)

        self.pack_start(scale, True, True, 3)
        self.pack_start(self.label, False, False, 3)

        self.show_all()
        self.__on_change(scale)
        scale.connect('value-changed', self.__on_change)

    def __on_change(self, widget):
        self.value = widget.get_value()
        label = "%s <span foreground='#999999'>%i %s</span>" % (self.caption,
            self.value, self.unit)
        self.label.set_markup(label)


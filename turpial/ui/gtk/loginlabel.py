# -*- coding: utf-8 -*-

""" Etiqueta de error de login del Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 21, 2009

import gtk
import cairo
import gobject

class LoginLabel(gtk.DrawingArea):
    def __init__(self, parent):
        gtk.DrawingArea.__init__(self)
        self.par = parent
        self.error = None
        self.active = False
        self.timer = None
        self.connect('expose-event', self.expose)
        self.set_size_request(30, 25)
    
    def deactivate(self):
        #if self.timer:
        #    gobject.source_remove(self.timer)
        self.error = None
        self.active = False
        self.queue_draw()
        
    def set_error(self, error):
        self.error = error
        self.active = True
        #if self.timer:
        #    gobject.source_remove(self.timer)
        #self.timer = gobject.timeout_add(5000, self.deactivate)
        self.queue_draw()
        
    def expose(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_line_width(0.8)
        rect = self.get_allocation()
        
        cr.rectangle(event.area.x, event.area.y, event.area.width,
                     event.area.height)
        cr.clip()
        
        cr.rectangle(0, 0, rect.width, rect.height)
        if not self.active:
            return
        
        cr.set_source_rgb(0, 0, 0)
        cr.fill()
        cr.select_font_face('Courier', cairo.FONT_SLANT_NORMAL,
                            cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(12)
        cr.set_source_rgb(1, 0.87, 0)
        cr.move_to(10, 15)
        
        cr.text_path(self.error)
        cr.stroke()
        
        #cr.show_text(self.error)

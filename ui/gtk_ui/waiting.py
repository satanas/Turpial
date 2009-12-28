# -*- coding: utf-8 -*-

# Indicador de progreso del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 20, 2009

import gtk
import cairo
import gobject

from ui import util as util

class CairoWaiting(gtk.DrawingArea):
    def __init__(self, parent):
        gtk.DrawingArea.__init__(self)
        self.par = parent
        self.active = False
        self.error = False
        self.connect('expose-event', self.expose)
        self.set_size_request(16, 16)
        self.timer = None
        self.count = 0
    
    def start(self):
        self.active = True
        self.error = False
        self.timer = gobject.timeout_add(150, self.update)
        self.queue_draw()
        
    def stop(self, error=False):
        self.active = error
        self.error = error
        self.queue_draw()
        if self.timer is not None: gobject.source_remove(self.timer)
        
        
    def update(self):
        self.count += 1
        if self.count > 3: self.count = 0
        self.queue_draw()
        return True
        
    def expose(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_line_width(0.8)
        rect = self.get_allocation()
        
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        
        cr.rectangle(0, 0, rect.width, rect.height)
        if not self.active: return
        
        if self.error:
            img = 'wait-error.png'
        else:
            img = 'wait2-%i.png' % (self.count + 1)
        pix = util.load_image(img, True)
        cr.set_source_pixbuf(pix, 0, 0)
        cr.paint()
        del pix
        
        #cr.text_path(self.error)
        #cr.stroke()

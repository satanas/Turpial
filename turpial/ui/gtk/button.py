# -*- coding: utf-8 -*-

# Botón con spinner de actividad para Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Sep 01, 2011

import gtk
import gobject

class SpinnerButton(gtk.Button):
    def __init__(self, parent, default_image):
        gtk.Button.__init__(self)
        self.mainwin = parent
        self.default_image = self.mainwin.load_image(default_image)
        self.set_image(self.default_image)
        self.count = 1
        self.timer = None
        
    def __update(self):
        self.count += 1
        if self.count > 31: 
            self.count = 1
        img = 'wait%i.png' % (self.count + 1)
        self.set_image(self.mainwin.load_image(img))
        return True
        
    def spin(self):
        self.set_sensitive(False)
        self.timer = gobject.timeout_add(30, self.__update)
    
    def stop(self):
        if self.timer is not None: 
            gobject.source_remove(self.timer)
        self.set_sensitive(True)
        self.set_image(self.default_image)
    

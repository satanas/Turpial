# -*- coding: utf-8 -*-

# Widget para mostrar una mensaje de error embebido en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 26, 2010

import gtk
##import gobject

class ErrorBox(gtk.HBox):
    def __init__(self, padding=0):
        gtk.HBox.__init__(self, False)
        
        ##self.timer = None
        
        self.message = gtk.Label()
        self.message.set_use_markup(True)
        self.message.set_markup("")
        
        lblalign = gtk.Alignment(xalign=0, yalign=0.5)
        lblalign.add(self.message)
        
        ttcolor = gtk.gdk.color_parse('#ebeab8')
        errorevent = gtk.EventBox()
        errorevent.add(lblalign)
        errorevent.modify_bg(gtk.STATE_NORMAL, ttcolor)
        errorevent.set_border_width(1)
        
        ttcolor = gtk.gdk.color_parse('#a88f53')
        errorevent2 = gtk.EventBox()
        errorevent2.add(errorevent)
        errorevent2.modify_bg(gtk.STATE_NORMAL, ttcolor)
        
        self.btn_close = gtk.Button()
        self.btn_close.set_relief(gtk.RELIEF_NONE)
        
        self.pack_start(errorevent2, True, True, padding)
        #self.pack_start(self.btn_close, False, False, padding)
        
        errorevent.connect('button-release-event', self.close)
        self.connect('expose-event', self.__show)
        
    def __show(self, widget=None, event=None):
        if self.message.get_label() == '':
            self.hide()
        else:
            gtk.HBox.show_all(self)
        
    def show(self):
        self.__show()
        
    def show_all(self):
        self.__show()
    
    def show_error(self, msg, show=True):
        if show:
            self.message.set_markup(u"<span size='small'>%s</span>" % msg)
            self.show()
            ##self.timer = gobject.timeout_add(6000, self.close)
        
    def hide(self):
        self.message.set_markup("")
        gtk.HBox.hide(self)
        
    def close(self, widget=None, event=None):
        self.hide()
        ##if self.timer:
        ##    gobject.source_remove(self.timer)
        
        

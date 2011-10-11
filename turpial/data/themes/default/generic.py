# -*- coding: utf-8 -*-

# Generic GTK dialog for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import os
import gtk
import time

from turpial.ui.gtk.htmlview import HtmlView

class GenericDialog(gtk.Window):
    def __init__(self, parent, title, content, width, height):
        gtk.Window.__init__(self)
        
        self.working = True
        self.mainwin = parent
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_title(title)
        self.set_resizable(False)
        self.set_size_request(width, height)
        self.set_transient_for(parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.container = HtmlView()
        self.container.render(content)
        
        box = gtk.VBox(False, 0)
        box.pack_start(self.container, True, True, 0)
        
        self.add(box)
        
        self.connect('delete-event', self.unclose)
        self.container.connect('action-request', self.action_request)
        self.container.connect('link-request', self.link_request)
        self.quit_ = False
        self.rtn = None
        self.show_all()
        
    def run(self):
        while not self.quit_:
            while gtk.events_pending():
                gtk.main_iteration()
        self.hide()
        return self.rtn
    
    def unclose(self, widget, event=None):
        if not self.working:
            self.quit_ = True
            return True
        else:
            return False
    
    def action_request(self, action):
        pass
    
    def link_request(self, url):
        pass

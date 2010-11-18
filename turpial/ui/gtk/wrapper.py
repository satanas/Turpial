# -*- coding: utf-8 -*-

"""Contenedor genérico para los widgets del Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 21, 2009

import gtk

class WrapperAlign:
    left = 0
    middle = 1
    right = 2
    
class Wrapper(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        
        self.children = {
            WrapperAlign.left: None,
            WrapperAlign.middle: None,
            WrapperAlign.right: None,
        }
    
    def _append_widget(self, widget, align):
        self.children[align] = widget
        
    def change_mode(self, mode):
        for child in self.get_children():
            self.remove(child)
        
        if mode == 'wide':
            self.wrapper = gtk.HBox(True)
            
            for i in range(3):
                widget = self.children[i]
                if widget is None:
                    continue
                
                box = gtk.VBox(False)
                #box.pack_start(gtk.Label(widget.caption), False, False)
                if widget.get_parent(): 
                    widget.reparent(box)
                else:
                    box.pack_start(widget, True, True)
                self.wrapper.pack_start(box)
        else:
            self.wrapper = gtk.Notebook()
            
            for i in range(3):
                widget = self.children[i]
                if widget is None:
                    continue
                
                if widget.get_parent(): 
                    widget.reparent(self.wrapper)
                    self.wrapper.set_tab_label(widget,
                                               gtk.Label(widget.caption))
                else:
                    self.wrapper.append_page(widget, gtk.Label(widget.caption))
                
                self.wrapper.set_tab_label_packing(widget,
                                                   True, True, gtk.PACK_START)

        self.add(self.wrapper)
        self.show_all()
        
    def update_wrap(self, width, mode):
        # Reimplementar en la clase hija de ser necesario
        if mode == 'single':
            w = width
        else:
            w = width / 3
        
        for i in range(3):
            widget = self.children[i]
            if widget is None:
                continue
            
            widget.update_wrap(w)

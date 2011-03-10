# -*- coding: utf-8 -*-

# Widget para mostrar una columna estándar en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 25, 2010

import gtk
import logging

from turpial.ui import util as util
from turpial.ui.gtk.errorbox import ErrorBox
from turpial.ui.gtk.statuslist import StatusList
from turpial.ui.gtk.waiting import CairoWaiting

log = logging.getLogger('Gtk:Column')

class GenericColumn(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.mainwin = mainwin
        self.statuslist = StatusList(mainwin)
        self.waiting = CairoWaiting(mainwin)
        self.walign = gtk.Alignment(xalign=1, yalign=0.5)
        self.walign.add(self.waiting)
        self.errorbox = ErrorBox()
        self.label = gtk.Label(label)
        self.caption = label
        
        self.connect('expose-event', self.error_show)
        
    def error_show(self, widget, event):
        self.errorbox.show()
        
    def update_tweets(self, response):
        count = 0
        if response.type == 'error':
            self.stop_update(True, response.errmsg)
        else:
            statuses = response.items
            if len(statuses) == 0:
                self.statuslist.clear()
                self.stop_update(True, _('No tweets available'))
            else:
                count = self.statuslist.update(statuses)
                self.stop_update()
        self.on_update()
        return count
            
    def update_user_pic(self, user, pic):
        self.statuslist.update_user_pic(user, pic)
        
    def update_wrap(self, width):
        self.statuslist.update_wrap(width)
    
    def start_update(self):
        self.waiting.start()
        self.errorbox.hide()
        
    def stop_update(self, error=False, msg=''):
        self.waiting.stop(error)
        self.errorbox.show_error(msg, error)
    
    def clear(self):
        self.statuslist.clear()
    
    def on_update(self, data=None):
        pass
        
class StandardColumn(GenericColumn):
    def __init__(self, mainwin, label='', pos=None, viewed=None):
        GenericColumn.__init__(self, mainwin, label)
        
        self.pos = pos
        self.handler = None
        self.changing_col = False
        
        model = gtk.ListStore(str, str)
        cell = gtk.CellRendererText()
        self.listcombo = gtk.ComboBox()
        self.listcombo.pack_start(cell, True)
        self.listcombo.add_attribute(cell, 'text', 1)
        self.listcombo.set_model(model)
        
        self.refresh = gtk.Button()
        self.refresh.set_image(self.mainwin.load_image('action-refresh.png'))
        self.refresh.set_tooltip_text(_('Manual Update'))
        
        self.mark_all = gtk.Button()
        self.mark_all.set_image(self.mainwin.load_image('action-mark-all.png'))
        self.mark_all.set_tooltip_text(_('Mark all as read'))
        
        listsbox = gtk.HBox(False)
        listsbox.pack_start(self.mark_all, False, False)
        listsbox.pack_start(self.listcombo, True, True)
        listsbox.pack_start(self.refresh, False, False)
        listsbox.pack_start(self.walign, False, False, 2)
        
        self.pack_start(listsbox, False, False)
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.statuslist, True, True)
        
        self.refresh.connect('clicked', self.__manual_update)
        self.mark_all.connect('clicked', self.__mark_all_as_read)
        
    def __manual_update(self, widget):
        self.mainwin.manual_update(self.pos)
        
    def __mark_all_as_read(self, widget):
        self.statuslist.mark_all_as_read()
        
    def __change_list(self, widget):
        model = self.listcombo.get_model()
        iter = self.listcombo.get_active_iter()
        new_id = model.get_value(iter, 0)
        self.caption = model.get_value(iter, 1)
        self.changing_col = True
        self.label.set_label(self.caption)
        try:
            self.get_parent().set_tab_label(self, self.label)
        except:
            pass
        self.mainwin.request_change_column(self.pos, new_id)
        
    def fill_combo(self, columns, new_viewed):
        self.viewed = new_viewed[self.pos]
        
        i = 0
        default = -1
        model = self.listcombo.get_model()
        fixed = ['timeline', 'replies', 'directs','sent']
        for key in fixed:
            model.append([key, columns[key].title])
            if key == self.viewed.id:
                default = i
            i += 1
            
        for key in sorted(columns.iterkeys()):
            if key in fixed:
                continue
            model.append([key, columns[key].title])
            if key == self.viewed.id:
                default = i
            i += 1
        
        self.last_index = default
        self.listcombo.set_model(model)
        self.listcombo.set_active(self.last_index)
        iter = self.listcombo.get_active_iter()
        self.caption = model.get_value(iter, 1)
        self.label = gtk.Label(self.caption)
        self.handler = self.listcombo.connect('changed', self.__change_list)
        
    def set_combo_item(self, reset=False):
        self.listcombo.disconnect(self.handler)
        if reset:
            self.listcombo.set_active(self.last_index)
        else:
            self.last_index = self.listcombo.get_active()
            
            if self.changing_col:
                model = self.listcombo.get_model()
                iter = self.listcombo.get_active_iter()
                new_id = model.get_value(iter, 0)
                
                new_config = {'Columns': {}}
                column = 'column%i' % (self.pos + 1)
                new_config['Columns'][column] = new_id
                self.mainwin.save_config(new_config)
        
        self.changing_col = False
        self.handler = self.listcombo.connect('changed', self.__change_list)
        
    def start_update(self):
        self.waiting.start()
        self.errorbox.hide()
        self.refresh.set_sensitive(False)
        self.listcombo.set_sensitive(False)
        self.mark_all.set_sensitive(False)
        
    def stop_update(self, error=False, msg=''):
        if error:
            self.set_combo_item(True)
        else:
            self.set_combo_item()
        self.waiting.stop(error)
        self.errorbox.show_error(msg, error)
        self.refresh.set_sensitive(True)
        self.listcombo.set_sensitive(True)
        self.mark_all.set_sensitive(True)
        
class SingleColumn(GenericColumn):
    def __init__(self, mainwin, label=''):
        GenericColumn.__init__(self, mainwin, label)
        
        #self.errorbox = gtk.HBox(False)
        #self.errorbox.pack_start(self.lblerror, False, False, 2)
        #self.errorbox.pack_start(self.walign, False, False, 2)
        
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.statuslist, True, True)
        
class SearchColumn(GenericColumn):
    def __init__(self, mainwin, label=''):
        GenericColumn.__init__(self, mainwin, label)
        
        self.input_topics = gtk.Entry()
        self.clearbtn = gtk.Button()
        self.clearbtn.set_image(self.mainwin.load_image('action-clear.png'))
        self.clearbtn.set_tooltip_text(_('Clear results'))
        #self.clearbtn.set_relief(gtk.RELIEF_NONE)
        try:
            #self.input_topics.set_property("primary-icon-stock", 
            #                               gtk.STOCK_FIND)
            self.input_topics.set_property("secondary-icon-stock",
                                           gtk.STOCK_FIND)
            self.input_topics.connect("icon-press", self.__on_icon_press)
        except: 
            pass
        
        inputbox = gtk.HBox(False)
        inputbox.pack_start(self.input_topics, True, True)
        inputbox.pack_start(self.clearbtn, False, False)
        inputbox.pack_start(self.walign, False, False, 2)
        
        self.pack_start(inputbox, False, False)
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.statuslist, True, True)
        
        self.clearbtn.connect('clicked', self.__clear)
        self.input_topics.connect('activate', self.__search_topic)
        self.input_topics.grab_focus()
        
    def __on_icon_press(self, widget, pos, e):
        #if pos == 0: 
        #    self.__search_topic(widget)
        if pos == 1:
            #widget.set_text('')
            self.__search_topic(widget)
            
    def __clear(self, widget):
        self.statuslist.clear()
        self.input_topics.grab_focus()
        
    def __search_topic(self, widget):
        topic = widget.get_text()
        if topic != '':
            self.lock()
            self.mainwin.request_search(topic)
            widget.set_text('')
        else:
            widget.set_text(_('You must write something to search'))
            widget.grab_focus()
        
    def on_update(self, data=None):
        self.unlock()
        
    def lock(self):
        self.input_topics.set_sensitive(False)
        self.clearbtn.set_sensitive(False)
        
    def unlock(self):
        self.input_topics.set_sensitive(True)
        self.clearbtn.set_sensitive(True)


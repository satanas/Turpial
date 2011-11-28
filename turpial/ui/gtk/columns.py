# -*- coding: utf-8 -*-

# GTK columns manager for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 26, 2011

import os
import gtk
import logging

from turpial.ui.lang import i18n
from turpial.ui.html import HtmlParser
from turpial.ui.gtk.htmlview import HtmlView
from turpial.ui.gtk.account_form import AccountForm

from libturpial.api.models.column import Column

log = logging.getLogger('Gtk')

class ColumnsDialog(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.mainwin = parent
        self.core = self.mainwin.core
        self.htmlparser = HtmlParser()
        self.set_title(i18n.get('columns'))
        self.set_size_request(480, 300)
        self.set_resizable(False)
        self.set_icon(self.mainwin.load_image('turpial.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        
        self.container = HtmlView()
        self.container.connect('action-request', self.__action_request)
        self.add(self.container)
        self.showed = False
        self.form = None
    
    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True
    
    def __action_request(self, widget, url):
        action, args = self.htmlparser.parse_command(url)
        
        if action == "close":
            self.__close(widget)
        elif action == "new_column":
            column = self.htmlparser.render_new_column(self.mainwin.get_all_accounts(),
                int(args[0]))
            extra = "activate_change_trigger();"
            self.container.append_element('#list', column, extra)
        elif action == "save_columns":
            columns = []
            col_data = args[0].split('^')
            for col in col_data:
                id_ = col.split('|')[0]
                acc_id = col.split('|')[1].split('-')[0]
                pt_id = col.split('|')[1].split('-')[1]
                col_id = col.split('|')[2]
                columns.append(Column(id_, acc_id, pt_id, col_id))
            self.mainwin.save_columns(columns)
            self.__close(widget)
            
    def update(self):
        if self.showed:
            page = self.htmlparser.columns(self.mainwin.get_all_accounts(),
                self.mainwin.get_registered_columns(), self.mainwin.get_all_columns())
            self.container.render(page)
    
    def cancel_login(self, message):
        if self.form:
            self.form.cancel(message)
            return True
        return False
    
    def done_login(self):
        if self.form:
            self.form.done()
            return True
        return False
    
    def show(self):
        if self.showed:
            self.present()
        else:
            self.showed = True
            self.update()
            self.show_all()
    
    def quit(self):
        self.destroy()

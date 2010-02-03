# -*- coding: utf-8 -*-

# Widget para mostrar respuestas de un tweet en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Feb 02, 2010

import gtk

from waiting import*
from tweetslist import *
from ui import util as util

class ReplyBox(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.mainwin = parent
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_title('En respuesta a...')
        self.set_resizable(False)
        self.set_size_request(500, 150)
        self.set_transient_for(parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        self.tweets = TweetList(parent, 'En respuesta a...')
        
        top = gtk.VBox(False)
        top.pack_start(self.tweets, True, True, 5)
        
        vbox = gtk.VBox(False)
        vbox.pack_start(top, False, False, 2)
        #vbox.pack_start(updatebox, True, True, 2)
        #vbox.pack_start(bottom, False, False, 2)
        #vbox.pack_start(self.toolbox, False, False, 2)
        
        self.add(vbox)
        
        self.connect('delete-event', self.__unclose)
        self.connect('size-request', self.__size_request)
        self.show_all()
    
    def __size_request(self, widget, event, data=None):
        w, h = self.get_size()
        self.tweets.update_wrap(w, 'single')
        
    def __unclose(self, widget, event=None):
        
        return False
        
    def show(self, text, id, user):
        self.in_reply_id = id
        self.in_reply_user = user
        if id != '' and user != '':
            self.label.set_markup('<span size="medium"><b>En respuesta a %s</b></span>' % user)
        
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_focus(self.update_text)
        buffer = self.update_text.get_buffer()
        buffer.set_text(text)
        self.show_all()
        
    def clear(self, widget):
        self.update_text.get_buffer().set_text('')
        
    def update(self, widget):
        buffer = self.update_text.get_buffer()
        start, end = buffer.get_bounds()
        tweet = buffer.get_text(start, end)
        if tweet == '': 
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>Eyy... debes escribir algo</span>")
            return
        
        self.waiting.start()
        self.mainwin.request_update_status(tweet, self.in_reply_id)
        self.block()
        
    def show_options(self, widget, event=None):
        self.url.set_text('')
        self.url.grab_focus()

# -*- coding: utf-8 -*-

# Widget para mostrar una columna estándar en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 25, 2010

import gtk
import pango
import gobject
import logging

from turpial.ui import util as util
from turpial.ui.gtk.errorbox import ErrorBox
from turpial.ui.gtk.statuslist import StatusList
from turpial.ui.gtk.waiting import CairoWaiting

log = logging.getLogger('Gtk:Column')

class StandardColumn(gtk.VBox):
    def __init__(self, mainwin, label='', menu='normal'):
        gtk.VBox.__init__(self, False)
        
        self.last = None    # Last tweets updated
        
        self.mainwin = mainwin
        self.tweetlist = StatusList(mainwin, menu)
        
        self.waiting = CairoWaiting(mainwin)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        '''
        self.lblerror = gtk.Label()
        self.lblerror.set_use_markup(True)
        self.errorbox = gtk.HBox(False)
        self.errorbox.pack_start(self.lblerror, False, False, 2)
        '''
        
        self.errorbox = ErrorBox()
        self.label = gtk.Label(label)
        self.caption = label
        
        self.listcombo = gtk.combo_box_new_text()
        self.listcombo.append_text('Lista de prueba 1')
        self.listcombo.append_text('Lista de prueba 2')
        
        self.refresh = gtk.Button()
        self.refresh.set_image(self.mainwin.load_image('refresh.png'))
        #self.refresh.set_relief(gtk.RELIEF_NONE)
        
        listsbox = gtk.HBox(False)
        listsbox.pack_start(self.listcombo, True, True)
        listsbox.pack_start(self.refresh, False, False)
        listsbox.pack_start(align, False, False, 2)
        
        self.pack_start(listsbox, False, False)
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.tweetlist, True, True)
        
        self.connect('expose-event', self.error_show)
        
    def error_show(self, widget, event):
        self.errorbox.show()
        
    def update_tweets(self, response):
        if response.type == 'error':
            self.stop_update(True, response.errmsg)
            return 0
            
        arr_tweets = response.items
        if len(arr_tweets) == 0:
            self.tweetlist.clear()
            self.stop_update(True, _('No tweets available'))
            return 0
        else:
            count = util.count_new_tweets(arr_tweets, self.last)
            self.stop_update()
            self.tweetlist.clear()
            for tweet in arr_tweets:
                self.tweetlist.add_tweet(tweet)
            self.last = arr_tweets
            
            return count
            
    def update_user_pic(self, user, pic):
        self.tweetlist.update_user_pic(user, pic)
        
    def update_wrap(self, width):
        self.tweetlist.update_wrap(width)
    
    def start_update(self):
        self.waiting.start()
        self.errorbox.hide()
        
    def stop_update(self, error=False, msg=''):
        self.waiting.stop(error)
        self.errorbox.show_error(msg, error)

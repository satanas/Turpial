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

class StandardColumn(gtk.VBox):
    def __init__(self, mainwin, label='', menu='normal'):
        gtk.VBox.__init__(self, False)
        
        self.last = None    # Last tweets updated
        
        self.mainwin = mainwin
        self.tweetlist = StatusList(mainwin, menu)
        
        self.waiting = CairoWaiting(mainwin)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
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
        
class SingleColumn(gtk.VBox):
    def __init__(self, mainwin, label='', menu='normal'):
        gtk.VBox.__init__(self, False)
        
        self.last = None    # Last tweets updated
        
        self.mainwin = mainwin
        self.tweetlist = StatusList(mainwin, menu)
        self.lblerror = gtk.Label()
        self.lblerror.set_use_markup(True)
        self.waiting = CairoWaiting(mainwin)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        self.label = gtk.Label(label)
        self.caption = label
        
        self.errorbox = gtk.HBox(False)
        self.errorbox.pack_start(self.lblerror, False, False, 2)
        self.errorbox.pack_start(align, False, False, 2)
        
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
        self.lblerror.set_markup("")
        self.errorbox.hide()
        
    def stop_update(self, error=False, msg=''):
        self.waiting.stop(error)
        self.lblerror.set_markup(u"<span size='small'>%s</span>" % msg)
        if error:
            self.errorbox.show()
        else:
            self.errorbox.hide()
            
    def clear(self):
        self.tweetlist.clear()
        
class SearchColumn(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.last = None    # Last tweets updated
        
        self.mainwin = mainwin
        self.input_topics = gtk.Entry()
        self.clearbtn = gtk.Button()
        self.clearbtn.set_image(self.mainwin.load_image('button-clear.png'))
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
        
        self.tweetlist = StatusList(mainwin)
        
        self.waiting = CairoWaiting(mainwin)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        inputbox = gtk.HBox(False)
        inputbox.pack_start(self.input_topics, True, True)
        inputbox.pack_start(self.clearbtn, False, False)
        inputbox.pack_start(align, False, False, 2)
        
        self.label = gtk.Label(label)
        self.caption = label
        
        self.errorbox = ErrorBox()
        
        self.pack_start(inputbox, False, False)
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.tweetlist, True, True)
        self.show_all()
        
        self.clearbtn.connect('clicked', self.__clear)
        self.input_topics.connect('activate', self.__search_topic)
        self.input_topics.grab_focus()
        self.connect('expose-event', self.error_show)
        
    def __on_icon_press(self, widget, pos, e):
        #if pos == 0: 
        #    self.__search_topic(widget)
        if pos == 1:
            #widget.set_text('')
            self.__search_topic(widget)
            
    def __clear(self, widget):
        self.tweetlist.clear()
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
        
    def error_show(self, widget, event):
        self.errorbox.show()
        
    def update_tweets(self, response):
        if response.type == 'error':
            self.stop_search(True, response.errmsg)
            self.unlock()
            return 0
            
        arr_tweets = response.items
        if len(arr_tweets) == 0:
            self.tweetlist.clear()
            self.stop_search(True, _('No tweets available'))
        else:
            self.stop_search()
            self.tweetlist.clear()
            for tweet in arr_tweets:
                self.tweetlist.add_tweet(tweet)
            
        self.unlock()
        return 0
        
    def update_user_pic(self, user, pic):
        self.tweetlist.update_user_pic(user, pic)
        
    def update_wrap(self, width):
        self.tweetlist.update_wrap(width)
        
    def start_search(self):
        self.waiting.start()
        self.errorbox.hide()
        
    def stop_search(self, error=False, msg=''):
        self.waiting.stop(error)
        self.errorbox.show_error(msg, error)
        
    def lock(self):
        self.input_topics.set_sensitive(False)
        self.clearbtn.set_sensitive(False)
        
    def unlock(self):
        self.input_topics.set_sensitive(True)
        self.clearbtn.set_sensitive(True)


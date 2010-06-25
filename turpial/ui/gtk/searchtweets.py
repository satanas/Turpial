# -*- coding: utf-8 -*-

"""Widget para mostrar resultados de una búsqueda en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Ene 06, 2010

import gtk

from turpial.ui.gtk.tweetslist import TweetList
from turpial.ui.gtk.waiting import CairoWaiting

class SearchTweets(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.last = None    # Last tweets updated
        
        self.mainwin = mainwin
        self.input_topics = gtk.Entry()
        self.clearbtn = gtk.Button()
        self.clearbtn.set_image(self.mainwin.load_image('clear.png'))
        self.clearbtn.set_tooltip_text(_('Clear results'))
        try:
            #self.input_topics.set_property("primary-icon-stock", 
            #                               gtk.STOCK_FIND)
            self.input_topics.set_property("secondary-icon-stock",
                                           gtk.STOCK_FIND)
            self.input_topics.connect("icon-press", self.__on_icon_press)
        except: 
            pass
        
        self.tweetlist = TweetList(mainwin)
        
        self.lblerror = gtk.Label()
        self.lblerror.set_use_markup(True)
        
        self.waiting = CairoWaiting(mainwin)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        inputbox = gtk.HBox(False)
        inputbox.pack_start(self.input_topics, True, True)
        inputbox.pack_start(self.clearbtn, False, False)
        
        self.label = gtk.Label(label)
        self.caption = label
        
        self.errorbox = gtk.HBox(False)
        self.errorbox.pack_start(self.lblerror, False, False, 2)
        self.errorbox.pack_start(align, False, False, 2)
        
        self.pack_start(inputbox, False, False)
        self.pack_start(self.errorbox, False, False)
        self.pack_start(self.tweetlist, True, True)
        self.show_all()
        #self.errorbox.hide()
        
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
        self.lblerror.set_markup("")
        
    def stop_search(self, error=False, msg=''):
        self.waiting.stop(error)
        self.lblerror.set_markup(u"<span size='small'>%s</span>" % msg)
            
    def lock(self):
        self.input_topics.set_sensitive(False)
        self.clearbtn.set_sensitive(False)
        
    def unlock(self):
        self.input_topics.set_sensitive(True)
        self.clearbtn.set_sensitive(True)

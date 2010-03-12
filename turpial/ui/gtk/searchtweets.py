# -*- coding: utf-8 -*-

# Widget para mostrar resultados de una búsqueda en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Ene 06, 2010

import gtk

from turpial.ui.gtk.tweetslist import *

class SearchTweets(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.mainwin = mainwin
        self.input_topics = gtk.Entry()
        self.clearbtn = gtk.Button()
        self.clearbtn.set_image(self.mainwin.load_image('clear.png'))
        self.clearbtn.set_tooltip_text('Limpiar todos los resultados')
        try:
            #self.input_topics.set_property("primary-icon-stock", gtk.STOCK_FIND)
            self.input_topics.set_property("secondary-icon-stock", gtk.STOCK_FIND)
            self.input_topics.connect("icon-press", self.__on_icon_press)
        except: 
            pass
        
        inputbox = gtk.HBox(False)
        inputbox.pack_start(self.input_topics, True, True)
        inputbox.pack_start(self.clearbtn, False, False)
        
        self.topics = TweetList(mainwin, label)
        self.caption = label
        
        self.pack_start(inputbox, False, False)
        self.pack_start(self.topics, True, True)
        self.show_all()
        
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
        self.topics.clear()
        self.input_topics.grab_focus()
        
    def __search_topic(self, widget):
        topic = widget.get_text()
        self.mainwin.request_search_topic(topic)
        widget.set_text('')
        widget.grab_focus()
        
    def update_tweets(self, arr_tweets):
        self.topics.update_tweets(arr_tweets)
        
    def update_user_pic(self, user, pic):
        self.topics.update_user_pic(user, pic)
        
    def update_wrap(self, width):
        self.topics.update_wrap(width)

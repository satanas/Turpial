# -*- coding: utf-8 -*-

# Widget que representa las tres columnas del Profile en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 03, 2010

from turpial.ui.gtk.userform import  UserForm
from turpial.ui.gtk.tweetslist import TweetList
from turpial.ui.gtk.searchtweets import SearchTweets
from turpial.ui.gtk.wrapper import Wrapper, WrapperAlign

class Profile(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.favorites = TweetList(mainwin, _('Favorites'))
        self.user_form = UserForm(mainwin, _('Profile'))
        self.topics = SearchTweets(mainwin, _('Search'))
        
        self._append_widget(self.user_form, WrapperAlign.left)
        self._append_widget(self.favorites, WrapperAlign.middle)
        self._append_widget(self.topics, WrapperAlign.right)
        
        self.change_mode(mode)
        
    def set_user_profile(self, user_profile):
        self.user_form.update(user_profile)

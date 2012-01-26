# -*- coding: utf-8 -*-

# Widget que representa las tres columnas del Profile en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 03, 2010

from turpial.ui.gtk.userform import  UserForm
from turpial.ui.gtk.wrapper import Wrapper, WrapperAlign
from turpial.ui.gtk.columns import SingleColumn, SearchColumn

class Profile(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.favorites = SingleColumn(mainwin, _('Favorites'))
        self.user_form = UserForm(mainwin, _('Profile'))
        self.search = SearchColumn(mainwin, _('Search'))
        
        self._append_widget(self.user_form, WrapperAlign.left)
        self._append_widget(self.favorites, WrapperAlign.middle)
        self._append_widget(self.search, WrapperAlign.right)
        
        self.change_mode(mode)
        
    def set_user_profile(self, user_profile):
        self.user_form.update(user_profile)

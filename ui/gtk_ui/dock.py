# -*- coding: utf-8 -*-

# Dock para los botones principales del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 20, 2009

import gtk

from about import *
from ui import util as util

class Dock(gtk.Alignment):
    def __init__(self, parent, mode='single'):
        gtk.Alignment.__init__(self, 0.5, 0.5)
        
        self.mainwin = parent
        
        self.btn_home = gtk.Button()
        self.btn_home.set_relief(gtk.RELIEF_NONE)
        self.btn_home.set_tooltip_text('Home')
        self.btn_favs = gtk.Button()
        self.btn_favs.set_relief(gtk.RELIEF_NONE)
        self.btn_favs.set_tooltip_text('Favorites')
        #self.btn_lists = gtk.Button()
        #self.btn_lists.set_relief(gtk.RELIEF_NONE)
        #self.btn_lists.set_tooltip_text('Retweets')
        self.btn_update = gtk.Button()
        self.btn_update.set_relief(gtk.RELIEF_NONE)
        self.btn_update.set_tooltip_text('Tweet')
        self.btn_search = gtk.Button()
        self.btn_search.set_relief(gtk.RELIEF_NONE)
        self.btn_search.set_tooltip_text('Search')
        self.btn_profile = gtk.Button()
        self.btn_profile.set_relief(gtk.RELIEF_NONE)
        self.btn_profile.set_tooltip_text('Profile')
        self.btn_settings = gtk.Button()
        self.btn_settings.set_relief(gtk.RELIEF_NONE)
        self.btn_settings.set_tooltip_text('Settings')
        self.btn_about = gtk.Button()
        self.btn_about.set_relief(gtk.RELIEF_NONE)
        self.btn_about.set_tooltip_text('About')
        
        self.btn_home.connect('clicked', self.mainwin.show_home)
        #self.btn_favs.connect('clicked', self.mainwin.show_favs)
        self.btn_update.connect('clicked', self.show_update)
        #self.btn_search.connect('clicked', self.mainwin.show_search)
        self.btn_profile.connect('clicked', self.mainwin.show_profile)
        self.btn_settings.connect('clicked', self.mainwin.show_preferences)
        self.btn_about.connect('clicked', self.__show_about)
        
        box = gtk.HBox()
        box.pack_start(self.btn_home, False, False)
        box.pack_start(self.btn_profile, False, False)
        box.pack_start(self.btn_update, False, False)
        box.pack_start(self.btn_settings, False, False)
        box.pack_start(self.btn_about, False, False)
        
        self.change_mode(mode)
        self.add(box)
        self.show_all()
        
    def __show_about(self, widget):
        about = About(self.mainwin)
        
    def show_update(self, widget):
        self.mainwin.show_update_box()
        
    def change_mode(self, mode):
        if mode == 'wide':
            self.btn_home.set_image(util.load_image('home.png'))
            #self.btn_favs.set_image(util.load_image('favorites.png'))
            #self.btn_lists.set_image(util.load_image('lists.png'))
            self.btn_update.set_image(util.load_image('button-update.png'))
            #self.btn_search.set_image(util.load_image('search.png'))
            self.btn_profile.set_image(util.load_image('profile.png'))
            self.btn_settings.set_image(util.load_image('settings.png'))
            self.btn_about.set_image(util.load_image('about.png'))
        else:
            self.btn_home.set_image(util.load_image('home-single.png'))
            #self.btn_favs.set_image(util.load_image('favorites-single.png'))
            #self.btn_lists.set_image(util.load_image('lists-single.png'))
            self.btn_update.set_image(util.load_image('button-update-single.png'))
            #self.btn_search.set_image(util.load_image('search-single.png'))
            self.btn_profile.set_image(util.load_image('profile-single.png'))
            self.btn_settings.set_image(util.load_image('settings-single.png'))
            self.btn_about.set_image(util.load_image('about-single.png'))

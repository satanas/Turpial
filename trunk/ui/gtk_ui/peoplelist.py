# -*- coding: utf-8 -*-

# Widget para mostrar perfiles como lista en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 21, 2009

import gtk
import pango

from ui import util as util

class PeopleList(gtk.ScrolledWindow):
    def __init__(self, mainwin, label=''):
        gtk.ScrolledWindow.__init__(self)
        
        self.mainwin = mainwin
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        
        self.label = gtk.Label(label)
        self.caption = label
        
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        self.add(self.list)
        
        # avatar, profile(pango), screen_name, name, url, location, bio, status, protected, following
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, str, str, str, str)
        self.list.set_model(self.model)
        cell_avatar = gtk.CellRendererPixbuf()
        cell_avatar.set_property('yalign', 0)
        self.cell_tweet = gtk.CellRendererText()
        self.cell_tweet.set_property('wrap-mode', pango.WRAP_WORD)
        self.cell_tweet.set_property('wrap-width', 260)
        self.cell_tweet.set_property('yalign', 0)
        self.cell_tweet.set_property('xalign', 0)
        
        column = gtk.TreeViewColumn('tweets')
        column.set_alignment(0.0)
        column.pack_start(cell_avatar, False)
        column.pack_start(self.cell_tweet, True)
        column.set_attributes(self.cell_tweet, markup=1)
        column.set_attributes(cell_avatar, pixbuf=0)
        self.list.append_column(column)
        
    def update_wrap(self, val):
        self.cell_tweet.set_property('wrap-width', val - 80)
        iter = self.model.get_iter_first()
        
        while iter:
            path = self.model.get_path(iter)
            self.model.row_changed(path, iter)
            iter = self.model.iter_next(iter)
            
    def update_user_pic(self, user, pic):
        # Evaluar si es más eficiente esto o cargar toda la lista cada vez
        pix = util.load_avatar(pic)
        iter = self.model.get_iter_first()
        while iter:
            u = self.model.get_value(iter, 1)
            if u == user:
                self.model.set_value(iter, 0, pix)
            iter = self.model.iter_next(iter)
        del pix
        
    def add_profile(self, p):
        username = p['screen_name']
        pix = self.mainwin.get_user_avatar(username, p['profile_image_url'])
        profile = util.get_pango_profile(p)
        
        self.model.append([pix, profile, username, p['name'], p['url'], 
            p['location'], p['description'], '', '', ''])
        del pix
        
    def update_profiles(self, people):
        self.model.clear()
        for p in people:
            self.add_profile(p)

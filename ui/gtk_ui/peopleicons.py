# -*- coding: utf-8 -*-

# Widget para mostrar contactos como iconos en el Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 21, 2009

import gtk
#import gobject

from ui import util as util

class PeopleIcons(gtk.ScrolledWindow):
    def __init__(self, mainwin, label='', named=False):
        gtk.ScrolledWindow.__init__(self)
        
        self.mainwin = mainwin
        self.named = named
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        
        # avatar, screen_name, pango_profile, pango_name, following
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, bool)
        
        self.list = gtk.IconView(self.model)
        self.list.set_pixbuf_column(0)
        try:
            self.list.set_has_tooltip(True)
        except:
            pass
        self.list.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.list.set_selection_mode(gtk.SELECTION_SINGLE)
        self.list.set_column_spacing(10)
        
        if self.named:
            self.list.set_markup_column(3)
            self.list.set_columns(2)
            self.list.set_item_width(120)
        else:
            self.list.set_columns(4)
            self.list.set_item_width(50)
        
        self.list.connect("query-tooltip", self.show_tooltip)
        self.list.connect("button-release-event", self.__popup_menu)
        
        self.label = gtk.Label(label)
        self.caption = label
        
        self.add(self.list)
        
    def __popup_menu(self, widget, event):
        paths = widget.get_selected_items()
        if (len(paths) == 0): return False
        
        row = self.model.get_iter(paths[0])
        if (event.button == 3):
            user = self.model.get_value(row, 1)
            following = self.model.get_value(row, 4)
            
            name = gtk.MenuItem('')
            name.get_child().set_markup("<b>@%s</b>" % user)
            name.set_sensitive(False)
            follow = gtk.MenuItem('Follow')
            unfollow = gtk.MenuItem('Unfollow')
            block = gtk.MenuItem('Block')
            #mute = gtk.MenuItem('Mute')
            #spam = gtk.MenuItem('Report as Spam')
            
            menu = gtk.Menu()
            menu.append(name)
            menu.append(gtk.SeparatorMenuItem())
            if following:
                menu.append(unfollow)
                
            else:
                menu.append(follow)
            #menu.append(block)
            
            follow.connect('activate', self.__manage, True, user)
            unfollow.connect('activate', self.__manage, False, user)
            
            menu.show_all()
            menu.popup(None, None, None, event.button ,event.time)
            
    def __manage(self, widget, follow, user):
        if follow:
            self.mainwin.request_follow(user)
        else:
            self.mainwin.request_unfollow(user)
        
    def show_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        rel_y = self.get_property('vadjustment').value
        
        path = widget.get_path_at_pos(int(x), int(y + rel_y))
        if path is None: return False
        
        model = widget.get_model()
        iter = model.get_iter(path)
        
        pix = model.get_value(iter, 0)
        tooltip.set_icon(pix)
        tooltip.set_markup(model.get_value(iter, 2))
        del pix
        
        return True
        
    def update_wrap(self, val):
        width = val - (self.list.get_margin() * 2) - 40
        item_w = self.list.get_item_width()
        
        columns = width / (item_w + self.list.get_column_spacing())
        self.list.set_columns(columns)
        
    def add_profile(self, p):
        #protected = ''
        #following = ''
        #if p['protected']: protected = '&lt;protected&gt;'
        follow = False
        if p['following']: 
            follow = True
        #    following = '&lt;following&gt;'
        
        pic = p['profile_image_url']
        username = p['screen_name']
        filename = self.mainwin.request_user_avatar(username, pic)
        if filename is None:
            pix = util.load_image('unknown.png', True)
        else:
            pix = util.load_avatar(filename)
        
        profile = util.get_pango_profile(p)
        
        '''
        # Escape pango markup
        for key in ['url', 'location', 'description', 'name', 'screen_name']:
            if not p.has_key(key) or p[key] is None: continue
            p[key] = gobject.markup_escape_text(p[key])
            
        profile = '<b>@%s</b> %s %s %s\n' % (p['screen_name'], p['name'], 
                following, protected)
        
        profile += '<span size="9000">'
        if not p['url'] is None: 
            profile += "<b>URL:</b> %s\n" % p['url']
            
        if not p['location'] is None:
            profile += "<b>Location:</b> %s\n" % p['location']
            
        if not p['description'] is None:
            profile += "<b>Bio:</b> %s\n" % p['description']
        
        if p.has_key('status'): 
            profile += '<span size="2000">\n</span>'
            status = '<span foreground="#999"><b>Last:</b> %s</span>\n' % (
                gobject.markup_escape_text(p['status']['text']))
            profile += status
        
        profile += '</span>'
        '''
        pangoname = '<span size="9000">@%s</span>' % p['screen_name']
        self.model.append([pix, username, profile, pangoname, follow])
        del pix
        
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
        
    def update_profiles(self, people):
        self.model.clear()
        for p in people:
            self.add_profile(p)

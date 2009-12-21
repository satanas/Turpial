# -*- coding: utf-8 -*-

# Vista para Turpial en PyGTK
#
# Author: Wil Alvarez (aka Satanas)
# Nov 08, 2009

import gtk
import util
import cairo
import pango
import logging
import gobject
import webbrowser

from base_ui import *
from gtkui import *

gtk.gdk.threads_init()

log = logging.getLogger('Gtk')

class WrapperAlign:
    left = 0
    middle = 1
    right = 2
    
class Wrapper(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        
        self.children = {
            WrapperAlign.left: None,
            WrapperAlign.middle: None,
            WrapperAlign.right: None,
        }
    
    def _append_widget(self, widget, align):
        self.children[align] = widget
        
    def change_mode(self, mode):
        for child in self.get_children():
            self.remove(child)
        
        if mode == 'wide':
            wrapper = gtk.HBox(True)
            
            for i in range(3):
                widget = self.children[i]
                if widget is None: continue
                
                box = gtk.VBox(False)
                box.pack_start(gtk.Label(widget.caption), False, False)
                if widget.get_parent(): 
                    widget.reparent(box)
                else:
                    box.pack_start(widget, True, True)
                wrapper.pack_start(box)
        else:
            wrapper = gtk.Notebook()
            
            for i in range(3):
                widget = self.children[i]
                if widget is None: continue
                
                if widget.get_parent(): 
                    widget.reparent(wrapper)
                    wrapper.set_tab_label(widget, gtk.Label(widget.caption))
                else:
                    wrapper.append_page(widget, gtk.Label(widget.caption))
                
                wrapper.set_tab_label_packing(widget, True, True, gtk.PACK_START)
            
        self.add(wrapper)
        self.show_all()
        
    def update_wrap(self, width, mode):
        # Reimplementar en la clase hija de ser necesario
        if mode == 'single':
            w = width
        else:
            w = width / 3
        
        for i in range(3):
            widget = self.children[i]
            if widget is None: continue
            
            widget.update_wrap(w)
        
class LoginLabel(gtk.DrawingArea):
    def __init__(self, parent):
        gtk.DrawingArea.__init__(self)
        self.par = parent
        self.error = None
        self.active = False
        self.connect('expose-event', self.expose)
        self.set_size_request(30, 25)
    
    def set_error(self, error):
        self.error = error
        self.active = True
        self.queue_draw()
        
    def expose(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_line_width(0.8)
        rect = self.get_allocation()
        
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        
        cr.rectangle(0, 0, rect.width, rect.height)
        if not self.active: return
        
        cr.set_source_rgb(0, 0, 0)
        cr.fill()
        cr.select_font_face('Courier', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(12)
        cr.set_source_rgb(1, 0.87, 0)
        cr.move_to(10, 15)
        
        cr.text_path(self.error)
        cr.stroke()
        
        #cr.show_text(self.error)
        

'''
class TweetList(gtk.ScrolledWindow):
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
        
        # avatar, username, datetime, client, pango_message, real_message, id, favorited, in_reply_to_id, in_reply_to_user, retweet_by
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str, str, str, 
            bool, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT)
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
        column.set_attributes(self.cell_tweet, markup=4)
        column.set_attributes(cell_avatar, pixbuf=0)
        self.list.append_column(column)
        
        self.list.connect("button-release-event", self.__popup_menu)
        
    def __highlight_hashtags(self, text):
        hashtags = util.detect_hashtags(text)
        if len(hashtags) == 0: return text
        
        for h in hashtags:
            torep = '#%s' % h
            cad = '<span foreground="#FF6633">#%s</span>' % h
            text = text.replace(torep, cad)
        return text
        
    def __highlight_mentions(self, text):
        mentions = util.detect_mentions(text)
        if len(mentions) == 0: return text
        
        for h in mentions:
            torep = '@%s' % h
            cad = '<span foreground="#FF6633">@%s</span>' % h
            text = text.replace(torep, cad)
        return text
        
    def __highlight_urls(self, text):
        urls = util.detect_urls(text)
        if len(urls) == 0: return text
        
        for u in urls:
            cad = '<span foreground="#FF6633">%s</span>' % u
            text = text.replace(u, cad)
        return text
        
    def __popup_menu(self, widget, event):
        model, row = widget.get_selection().get_selected()
        if (row is None): return False
        
        if (event.button == 3):
            user = model.get_value(row, 1)
            msg = model.get_value(row, 5)
            id = model.get_value(row, 6)
            fav = model.get_value(row, 7)
            
            re = "@%s " % user
            rt = "RT @%s %s" % (user, msg)
            
            profile = self.mainwin.request_user_profile()
            
            reply = gtk.MenuItem('Reply')
            retweet_old = gtk.MenuItem('Retweet')
            retweet = gtk.MenuItem('Retweet')
            save = gtk.MenuItem('+ Fav')
            unsave = gtk.MenuItem('- Fav')
            delete = gtk.MenuItem('Delete')
            open = gtk.MenuItem('Open URL')
            search = gtk.MenuItem('Search')
            
            urls = util.detect_urls(msg)
            open_menu = gtk.Menu()
            for u in urls:
                urlmenu = gtk.MenuItem(u)
                urlmenu.connect('activate', self.__open_url, u)
                open_menu.append(urlmenu)
            open.set_submenu(open_menu)
            
            menu = gtk.Menu()
            if profile['screen_name'] != user:
                menu.append(reply)
                menu.append(retweet_old)
                #menu.append(retweet)
            else:
                menu.append(delete)
            
            if fav:
                menu.append(unsave)
            else:
                menu.append(save)
            if len(urls) > 0: menu.append(open)
            #menu.append(search)
            
            reply.connect('activate', self.__show_update_box, re, id, user)
            retweet.connect('activate', self.__retweet, id)
            retweet_old.connect('activate', self.__show_update_box, rt)
            delete.connect('activate', self.__delete, id)
            save.connect('activate', self.__fav, True, id)
            unsave.connect('activate', self.__fav, False, id)
            
            menu.show_all()
            menu.popup(None, None, None, event.button ,event.time)
        
    def __open_url(self, widget, url):
        log.debug('Opening url %s' % url)
        webbrowser.open(url)
        
    def __show_update_box(self, widget, text, in_reply_id='', in_reply_user=''):
        self.mainwin.show_update_box(text, in_reply_id, in_reply_user)
        
    def __retweet(self, widget, id):
        self.mainwin.request_retweet(id)
        
    def __delete(self, widget, id):
        self.mainwin.request_destroy_status(id)
    
    def __fav(self, widget, fav, id):
        if fav:
            self.mainwin.request_fav(id)
        else:
            self.mainwin.request_unfav(id)
    
    def update_wrap(self, val):
        self.cell_tweet.set_property('wrap-width', val - 80)
        iter = self.model.get_iter_first()
        
        while iter:
            path = self.model.get_path(iter)
            self.model.row_changed(path, iter)
            iter = self.model.iter_next(iter)
        
    def add_tweet(self, tweet):
        #print tweet
        #print
        retweet_by = None
        if tweet.has_key('retweeted_status'):
            retweet_by = tweet['user']['screen_name']
            tweet = tweet['retweeted_status']
            
        if tweet.has_key('user'):
            username = tweet['user']['screen_name']
            avatar = tweet['user']['profile_image_url']
        elif tweet.has_key('sender'):
            username = tweet['sender']['screen_name']
            avatar = tweet['sender']['profile_image_url']
        elif tweet.has_key('from_user'):
            username = tweet['from_user']
            avatar = tweet['profile_image_url']
            
        client = util.detect_client(tweet)
        datetime = util.get_timestamp(tweet)
        
        pix = self.mainwin.get_user_avatar(username, avatar)
        #print 'message', tweet['text']
        message = gobject.markup_escape_text(tweet['text'])
        #message = tweet['text']
        message = '<span size="9000"><b>@%s</b> %s</span>' % (username, message)
        message = self.__highlight_hashtags(message)
        message = self.__highlight_mentions(message)
        message = self.__highlight_urls(message)
        interline = '<span size="2000">\n\n</span>'
        
        footer = '<span size="small" foreground="#999">%s' % datetime
        if client:
            footer += ' desde %s' % client
        
        in_reply_to_id = None
        in_reply_to_user = None
        if tweet.has_key('in_reply_to_status_id'):
            in_reply_to_id = tweet['in_reply_to_status_id']
            in_reply_to_user = tweet['in_reply_to_screen_name']
            if in_reply_to_user:
                footer += ' en respuesta a %s' % in_reply_to_user
        
        if retweet_by:
            footer += '\nRetweeted by %s' % retweet_by
            
        footer += '</span>'
        
        fav = False
        if tweet.has_key('favorited'): fav = tweet['favorited']
        
        pango_twt = message + interline + footer
        self.model.append([pix, username, datetime, client, pango_twt, tweet['text'],
            tweet['id'], fav, in_reply_to_id, in_reply_to_user, retweet_by])
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
        
    def update_tweets(self, arr_tweets):
        self.model.clear()
        for tweet in arr_tweets:
            self.add_tweet(tweet)
'''

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
        #self.label.set_size_request(val, -1)
        self.cell_tweet.set_property('wrap-width', val - 80)
        iter = self.model.get_iter_first()
        
        while iter:
            path = self.model.get_path(iter)
            self.model.row_changed(path, iter)
            iter = self.model.iter_next(iter)
            
    def add_profile(self, p):
        protected = ''
        following = ''
        if p['protected']: protected = '&lt;protected&gt;'
        if p['following']: protected = '&lt;following&gt;'
        
        pix = util.load_image('unknown.png', pixbuf=True)
        
        # Escape pango markup
        for key in ['url', 'location', 'description', 'name', 'screen_name']:
            if not p.has_key(key) or p[key] is None: continue
            p[key] = gobject.markup_escape_text(p[key])
            
        profile = '<span size="9000"><b>@%s</b> %s %s %s</span>\n' % (p['screen_name'], p['name'], 
                following, protected)
        profile += "<b>URL:</b> %s\n" % p['url']
        profile += "<b>Location:</b> %s\n" % p['location']
        profile += "<b>Bio:</b> %s\n" % p['description']
        profile += '<span size="2000">\n\n</span>'
        
        status = ''
        if p.has_key('status'): 
            status = '<span foreground="#999"><b>Last:</b> %s</span>\n' % (
                gobject.markup_escape_text(p['status']['text']))
        profile += status
        
        self.model.append([pix, profile, p['screen_name'], p['name'], p['url'], 
            p['location'], p['description'], status, protected, following])
        del pix
        
    def update_profiles(self, people):
        for p in people:
            self.add_profile(p)
            
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
        self.list.set_has_tooltip(True)
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
        protected = ''
        following = ''
        if p['protected']: protected = '&lt;protected&gt;'
        follow = False
        if p['following']: 
            follow = True
            following = '&lt;following&gt;'
        
        pic = p['profile_image_url']
        username = p['screen_name']
        filename = self.mainwin.request_user_avatar(username, pic)
        if filename is None:
            pix = util.load_image('unknown.png', True)
        else:
            pix = util.load_avatar(filename)
        
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
        for p in people:
            self.add_profile(p)
            
class SearchList(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.mainwin = mainwin
        self.input_topics = gtk.Entry()
        try:
            self.input_topics.set_property("primary-icon-stock", gtk.STOCK_FIND)
            self.input_topics.set_property("secondary-icon-stock", gtk.STOCK_CLEAR)
            self.input_topics.connect("icon-press", self.__on_icon_press)
        except: 
            pass
        
        inputbox = gtk.HBox(False)
        inputbox.pack_start(self.input_topics, True, True)
        
        self.topics = TweetList(mainwin, label)
        self.caption = label
        
        self.pack_start(inputbox, False, False)
        self.pack_start(self.topics, True, True)
        self.show_all()
        
        self.input_topics.connect('activate', self.__search_topic)
        
    def __on_icon_press(self, widget, pos, e):
        if pos == 0: 
            self.__search_topic(widget)
        elif pos == 1:
            widget.set_text('')
            
    def __search_topic(self, widget):
        topic = widget.get_text()
        self.mainwin.request_search_topic(topic)
        widget.set_text('')
        
    def update_tweets(self, arr_tweets):
        self.topics.update_tweets(arr_tweets)
        
    def update_user_pic(self, user, pic):
        self.topics.update_user_pic(user, pic)
        
    def update_wrap(self, width):
        self.topics.update_wrap(width)
        
class UserForm(gtk.VBox):
    def __init__(self, mainwin, label='', profile=None):
        gtk.VBox.__init__(self, False)
        
        label_width = 75
        self.mainwin = mainwin
        self.user = None
        self.label = gtk.Label(label)
        self.caption = label
        
        self.user_pic = gtk.Button()
        self.user_pic.set_size_request(60, 60)
        pic_box = gtk.VBox(False)
        pic_box.pack_start(self.user_pic, False, False, 10)
        
        self.screen_name = gtk.Label()
        self.screen_name.set_alignment(0, 0.5)
        self.tweets_count = gtk.Label()
        self.tweets_count.set_alignment(0, 0.5)
        self.tweets_count.set_padding(8, 0)
        self.following_count = gtk.Label()
        self.following_count.set_alignment(0, 0.5)
        self.following_count.set_padding(8, 0)
        self.followers_count = gtk.Label()
        self.followers_count.set_alignment(0, 0.5)
        self.followers_count.set_padding(8, 0)
        
        info_box = gtk.VBox(False)
        info_box.pack_start(self.screen_name, False, False, 5)
        info_box.pack_start(self.tweets_count, False, False)
        info_box.pack_start(self.following_count, False, False)
        info_box.pack_start(self.followers_count, False, False)
        
        top = gtk.HBox(False)
        top.pack_start(pic_box, False, False, 10)
        top.pack_start(info_box, False, False, 5)
        
        self.real_name = gtk.Entry()
        name_lbl = gtk.Label('Nombre')
        name_lbl.set_size_request(label_width, -1)
        name_box = gtk.HBox(False)
        name_box.pack_start(name_lbl, False, False, 2)
        name_box.pack_start(self.real_name, True, True, 5)
        
        self.location = gtk.Entry()
        loc_lbl = gtk.Label('Ubicacion')
        loc_lbl.set_size_request(label_width, -1)
        loc_box = gtk.HBox(False)
        loc_box.pack_start(loc_lbl, False, False, 2)
        loc_box.pack_start(self.location, True, True, 5)
        
        self.url = gtk.Entry()
        url_lbl = gtk.Label('URL')
        url_lbl.set_size_request(label_width, -1)
        url_box = gtk.HBox(False)
        url_box.pack_start(url_lbl, False, False, 2)
        url_box.pack_start(self.url, True, True, 5)
        
        self.bio = gtk.TextView()
        self.bio.set_wrap_mode(gtk.WRAP_WORD)
        scrollwin = gtk.ScrolledWindow()
        scrollwin.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        scrollwin.set_shadow_type(gtk.SHADOW_IN)
        scrollwin.set_size_request(-1, 80)
        scrollwin.add(self.bio)
        bio_lbl = gtk.Label('Bio')
        bio_lbl.set_size_request(label_width, -1)
        bio_box = gtk.HBox(False)
        bio_box.pack_start(bio_lbl, False, False, 2)
        bio_box.pack_start(scrollwin, True, True, 5)
        
        form = gtk.VBox(False)
        form.pack_start(name_box, False, False, 4)
        form.pack_start(loc_box, False, False, 4)
        form.pack_start(url_box, False, False, 4)
        form.pack_start(bio_box, False, False, 4)
        
        submit = gtk.Button(stock=gtk.STOCK_SAVE)
        submit_box = gtk.Alignment(1.0, 0.5)
        submit_box.set_property('right-padding', 5)
        submit_box.add(submit)
        
        self.pack_start(top, False, False)
        self.pack_start(form, False, False)
        self.pack_start(submit_box, False, False)
        
        submit.connect('clicked', self.save_user_profile)
        
    def update(self, profile):
        self.user = profile['screen_name']
        pix = self.mainwin.get_user_avatar(self.user, profile['profile_image_url'])
        avatar = gtk.Image()
        avatar.set_from_pixbuf(pix)
        self.user_pic.set_image(avatar)
        del pix
        self.screen_name.set_markup('<b>@%s</b>' % profile['screen_name'])
        self.tweets_count.set_markup('<span size="9000">%i Tweets</span>' % profile['statuses_count'])
        self.following_count.set_markup('<span size="9000">%i Following</span>' % profile['friends_count'])
        self.followers_count.set_markup('<span size="9000">%i Followers</span>' % profile['followers_count'])
        self.real_name.set_text(profile['name'])
        self.location.set_text(profile['location'])
        self.url.set_text(profile['url'])
        buffer = self.bio.get_buffer()
        buffer.set_text(profile['description'])
    
    def update_user_pic(self, user, pic):
        if self.user != user: return
        pix = util.load_avatar(pic, True)
        self.user_pic.set_image(pix)
        
    def save_user_profile(self, widget):
        self.real_name
        self.location
        self.url
        self.bio
        
    def update_wrap(self, w):
        pass
        
class Trending(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.caption = label
        
        currentlbl = gtk.Label('Current')
        
        currentbox = gtk.VBox(False)
        
    def update_wrap(self, w):
        pass
        
'''
class UpdateBox(gtk.Window):
    def __init__(self, parent):
        gtk.Window.__init__(self)
        
        self.mainwin = parent
        self.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.set_title('Update Status')
        self.set_resizable(False)
        #self.set_default_size(500, 120)
        self.set_size_request(500, 150)
        self.set_transient_for(parent)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        self.label = gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0.5)
        self.label.set_markup('<span size="medium"><b>What\'s happening?</b></span>')
        self.label.set_justify(gtk.JUSTIFY_LEFT)
        
        self.num_chars = gtk.Label()
        self.num_chars.set_use_markup(True)
        self.num_chars.set_markup('<span size="14000" foreground="#999"><b>140</b></span>')
        
        self.update_text = gtk.TextView()
        self.update_text.set_border_width(2)
        self.update_text.set_left_margin(2)
        self.update_text.set_right_margin(2)
        self.update_text.set_wrap_mode(gtk.WRAP_WORD)
        buffer = self.update_text.get_buffer()
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.update_text)
        
        updatebox = gtk.HBox(False)
        updatebox.pack_start(scroll, True, True, 3)
        
        self.url = gtk.Entry()
        btn_url = gtk.Button('Shorten URL')
        btn_url.set_tooltip_text('Shorten URL')
        #btn_url.set_relief(gtk.RELIEF_NONE)
        #btn_url.set_image(util.load_image('cut.png'))
        
        btn_pic = gtk.Button('Upload Pic')
        btn_pic.set_tooltip_text('Upload Pic')
        #btn_pic.set_relief(gtk.RELIEF_NONE)
        #btn_pic.set_image(util.load_image('photos.png'))
        
        tools = gtk.HBox(False)
        tools.pack_start(self.url, True, True, 3)
        tools.pack_start(btn_url, False, False)
        tools.pack_start(gtk.HSeparator(), False, False)
        tools.pack_start(btn_pic, False, False, 3)
        
        self.toolbox = gtk.Expander()
        self.toolbox.set_label('Opciones')
        self.toolbox.set_expanded(False)
        self.toolbox.add(tools)
        
        btn_clr = gtk.Button()
        btn_clr.set_image(util.load_image('clear.png'))
        btn_clr.set_tooltip_text('Clear Box')
        btn_clr.set_relief(gtk.RELIEF_NONE)
        btn_upd = gtk.Button('Update')
        chk_short = gtk.CheckButton('Autocortado de URLs')
        chk_short.set_sensitive(False)
        
        top = gtk.HBox(False)
        top.pack_start(self.label, True, True, 5)
        top.pack_start(self.num_chars, False, False, 5)
        
        self.waiting = CairoWaiting(self)
        
        buttonbox = gtk.HBox(False)
        buttonbox.pack_start(chk_short, False, False, 0)
        buttonbox.pack_start(btn_clr, False, False, 0)
        buttonbox.pack_start(gtk.HSeparator(), False, False, 2)
        buttonbox.pack_start(btn_upd, False, False, 0)
        abuttonbox = gtk.Alignment(1, 0.5)
        abuttonbox.add(buttonbox)
        
        bottom = gtk.HBox(False)
        bottom.pack_start(self.waiting, False, False, 5)
        bottom.pack_start(abuttonbox, True, True, 5)
        
        vbox = gtk.VBox(False)
        vbox.pack_start(top, False, False, 2)
        vbox.pack_start(updatebox, True, True, 2)
        vbox.pack_start(bottom, False, False, 2)
        vbox.pack_start(self.toolbox, False, False, 2)
        
        self.add(vbox)
        
        self.connect('delete-event', self.close)
        buffer.connect("changed", self.count_chars)
        btn_clr.connect('clicked', self.clear)
        btn_upd.connect('clicked', self.update)
        btn_url.connect('clicked', self.short_url)
        btn_pic.connect('clicked', self.upload_pic)
        self.toolbox.connect('activate', self.show_options)
    
    def show(self, text, id, user):
        self.in_reply_id = id
        self.in_reply_user = user
        if id != '' and user != '':
            self.label.set_markup('<span size="medium"><b>Reply to %s</b></span>' % user)
        
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        buffer = self.update_text.get_buffer()
        buffer.set_text(text)
        self.show_all()
        
    def close(self, widget=None, event=None):
        buffer = self.update_text.get_buffer()
        buffer.set_text('')
        self.url.set_text('')
        self.label.set_markup('<span size="medium"><b>What\'s happening?</b></span>')
        self.waiting.stop()
        self.toolbox.set_expanded(False)
        self.hide()
        return True
        
    def count_chars(self, widget):
        buffer = self.update_text.get_buffer()
        remain = 140 - buffer.get_char_count()
        
        if remain >= 20: color = "#999"
        elif 0 < remain < 20: color = "#d4790d"
        else: color = "#D40D12"
        
        self.num_chars.set_markup('<span size="14000" foreground="%s"><b>%i</b></span>' % (color, remain))
        
    def clear(self, widget):
        self.update_text.get_buffer().set_text('')
        
    def update(self, widget):
        buffer = self.update_text.get_buffer()
        start, end = buffer.get_bounds()
        tweet = buffer.get_text(start, end)
        
        self.mainwin.request_update_status(tweet, self.in_reply_id)
        self.close()
        
    def short_url(self, widget):
        self.waiting.start()
        self.mainwin.request_short_url(self.url.get_text(), self.update_shorten_url)
        
    def update_shorten_url(self, short):
        buffer = self.update_text.get_buffer()
        end_offset = buffer.get_property('cursor-position')
        start_offset = end_offset - 1
        
        end = buffer.get_iter_at_offset(end_offset)
        start = buffer.get_iter_at_offset(start_offset)
        text = buffer.get_text(start, end)
        
        if (text != ' ') and (start_offset > 0): short = ' ' + short
        
        buffer.insert_at_cursor(short)
        self.waiting.stop()
        self.toolbox.set_expanded(False)
        
    def upload_pic(self, widget):
        filtro = gtk.FileFilter()
        filtro.set_name('PNG, JPEG & GIF Images')
        filtro.add_pattern('*.png')
        filtro.add_pattern('*.gif')
        filtro.add_pattern('*.jpg')
        filtro.add_pattern('*.jpeg')
        
        dia = gtk.FileChooserDialog(title='Seleccione la imagen que desea subir',
            parent=self, action=gtk.FILE_CHOOSER_ACTION_OPEN, 
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OK, gtk.RESPONSE_OK))
        dia.add_filter(filtro)
        resp = dia.run()
        
        if resp == gtk.RESPONSE_OK:
            log.debug('Subiendo Imagen: %s' % dia.get_filename())
            ## self.mainwin.request_upload_pic(dia.get_filename())
        dia.destroy()
        
    def show_options(self, widget, event=None):
        self.url.set_text('')
        self.url.grab_focus()
'''

# ------------------------------------------------------------
# Objetos del Dock (Main Objects)
# ------------------------------------------------------------
class Home(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.timeline = TweetList(mainwin, 'Home')
        self.replies = TweetList(mainwin, 'Replies')
        self.direct = TweetList(mainwin, 'Direct')
        
        self._append_widget(self.timeline, WrapperAlign.left)
        self._append_widget(self.replies, WrapperAlign.middle)
        self._append_widget(self.direct, WrapperAlign.right)
        
        self.change_mode(mode)
        
class Favorites(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.favorites = TweetList(mainwin, 'Favorites')
        self.lfy = TweetList(mainwin, 'List following you')
        self.lyf = TweetList(mainwin, 'List you follow')
        
        self._append_widget(self.favorites, WrapperAlign.left)
        self._append_widget(self.lfy, WrapperAlign.middle)
        self._append_widget(self.lyf, WrapperAlign.right)
        
        self.change_mode(mode)
    
class Profile(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.user_form = UserForm(mainwin, 'Profile')
        self.following = PeopleIcons(mainwin, 'Following')
        self.followers = PeopleIcons(mainwin, 'Followers')
        
        self._append_widget(self.user_form, WrapperAlign.left)
        self._append_widget(self.following, WrapperAlign.middle)
        self._append_widget(self.followers, WrapperAlign.right)
        
        self.change_mode(mode)
        
    def set_user_profile(self, user_profile):
        self.user_form.update(user_profile)
        
    def set_following(self, arr_following):
        self.following.update_profiles(arr_following)
        
    def set_followers(self, arr_followers):
        self.followers.update_profiles(arr_followers)
        
class Search(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.trending = Trending(mainwin, 'Trending')
        self.topics = SearchList(mainwin, 'Search')
        self.people = PeopleList(mainwin, 'People')
        
        self._append_widget(self.trending, WrapperAlign.left)
        self._append_widget(self.topics, WrapperAlign.middle)
        self._append_widget(self.people, WrapperAlign.right)
        
        self.change_mode(mode)
        
'''
class CairoWaiting(gtk.DrawingArea):
    def __init__(self, parent):
        gtk.DrawingArea.__init__(self)
        self.par = parent
        self.active = False
        self.connect('expose-event', self.expose)
        self.set_size_request(16, 16)
        self.timer = None
        self.count = 0
    
    def start(self):
        self.active = True
        self.timer = gobject.timeout_add(150, self.update)
        self.queue_draw()
        
    def stop(self):
        self.active = False
        self.queue_draw()
        if self.timer is not None: gobject.source_remove(self.timer)
        
    def update(self):
        self.count += 1
        if self.count > 3: self.count = 0
        self.queue_draw()
        return True
        
    def expose(self, widget, event):
        cr = widget.window.cairo_create()
        cr.set_line_width(0.8)
        rect = self.get_allocation()
        
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()
        
        cr.rectangle(0, 0, rect.width, rect.height)
        if not self.active: return
        
        img = 'wait-%i.png' % (self.count + 1)
        pix = util.load_image(img, True)
        cr.set_source_pixbuf(pix, 0, 0)
        cr.paint()
        del pix
        
        #cr.text_path(self.error)
        #cr.stroke()
        
class Dock333(gtk.Alignment):
    def __init__(self, parent, mode='single'):
        gtk.Alignment.__init__(self, 0.5, 0.5)
        
        self.mainwin = parent
        
        self.btn_home = gtk.Button()
        self.btn_home.set_relief(gtk.RELIEF_NONE)
        self.btn_home.set_tooltip_text('Home')
        self.btn_favs = gtk.Button()
        self.btn_favs.set_relief(gtk.RELIEF_NONE)
        self.btn_favs.set_tooltip_text('Favoritos')
        self.btn_lists = gtk.Button()
        self.btn_lists.set_relief(gtk.RELIEF_NONE)
        self.btn_lists.set_tooltip_text('Listas')
        self.btn_update = gtk.Button()
        self.btn_update.set_relief(gtk.RELIEF_NONE)
        self.btn_update.set_tooltip_text('Actualizar Estado')
        self.btn_search = gtk.Button()
        self.btn_search.set_relief(gtk.RELIEF_NONE)
        self.btn_search.set_tooltip_text('Buscar')
        self.btn_profile = gtk.Button()
        self.btn_profile.set_relief(gtk.RELIEF_NONE)
        self.btn_profile.set_tooltip_text('Perfil')
        self.btn_settings = gtk.Button()
        self.btn_settings.set_relief(gtk.RELIEF_NONE)
        self.btn_settings.set_tooltip_text('Preferencias')
        
        self.btn_home.connect('clicked', self.mainwin.show_home)
        self.btn_favs.connect('clicked', self.mainwin.show_favs)
        self.btn_update.connect('clicked', self.show_update)
        self.btn_search.connect('clicked', self.mainwin.show_search)
        self.btn_profile.connect('clicked', self.mainwin.show_profile)
        self.btn_settings.connect('clicked', self.mainwin.switch_mode)
        
        box = gtk.HBox()
        box.pack_start(self.btn_home, False, False)
        box.pack_start(self.btn_favs, False, False)
        box.pack_start(self.btn_lists, False, False)
        box.pack_start(self.btn_update, False, False)
        box.pack_start(self.btn_search, False, False)
        box.pack_start(self.btn_profile, False, False)
        box.pack_start(self.btn_settings, False, False)
        
        self.change_mode(mode)
        self.add(box)
        self.show_all()
        
    def show_update(self, widget):
        self.mainwin.show_update_box()
        
    def change_mode(self, mode):
        if mode == 'wide':
            self.btn_home.set_image(util.load_image('home.png'))
            self.btn_favs.set_image(util.load_image('favorites.png'))
            self.btn_lists.set_image(util.load_image('lists.png'))
            self.btn_update.set_image(util.load_image('button-update.png'))
            self.btn_search.set_image(util.load_image('search.png'))
            self.btn_profile.set_image(util.load_image('profile.png'))
            self.btn_settings.set_image(util.load_image('settings.png'))
        else:
            self.btn_home.set_image(util.load_image('home-single.png'))
            self.btn_favs.set_image(util.load_image('favorites-single.png'))
            self.btn_lists.set_image(util.load_image('lists-single.png'))
            self.btn_update.set_image(util.load_image('button-update-single.png'))
            self.btn_search.set_image(util.load_image('search-single.png'))
            self.btn_profile.set_image(util.load_image('profile-single.png'))
            self.btn_settings.set_image(util.load_image('settings-single.png'))
'''

class Main(BaseGui, gtk.Window):
    def __init__(self, controller):
        BaseGui.__init__(self, controller)
        gtk.Window.__init__(self)
        
        self.set_title('Turpial')
        self.set_size_request(280, 350)
        self.set_default_size(320, 480)
        self.set_icon(util.load_image('turpial_icon.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect('destroy', self.quit)
        self.connect('size-request', self.size_request)
        
        self.mode = 0
        self.vbox = None
        self.workspace = 'wide'
        self.contentbox = gtk.VBox(False)
        
        self.home = Home(self, self.workspace)
        self.favs = Favorites(self)
        self.profile = Profile(self)
        self.search = Search(self)
        self.contenido = self.home
        self.updatebox = UpdateBox(self)
        
        self.dock = Dock(self, self.workspace)
        
    def quit(self, widget):
        self.hide()
        gtk.main_quit()
        self.request_signout()
        exit(0)
        
    def main_loop(self):
        gtk.main()
        
    def show_login(self):
        self.mode = 1
        if self.vbox is not None: self.remove(self.vbox)
        
        avatar = util.load_image('logo.png')
        self.message = LoginLabel(self)
        
        lbl_user = gtk.Label()
        lbl_user.set_justify(gtk.JUSTIFY_LEFT)
        lbl_user.set_use_markup(True)
        lbl_user.set_markup('<span size="small">Username</span>')
        
        lbl_pass = gtk.Label()
        lbl_pass.set_justify(gtk.JUSTIFY_LEFT)
        lbl_pass.set_use_markup(True)
        lbl_pass.set_markup('<span size="small">Password</span>')
        
        self.username = gtk.Entry()
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        
        self.btn_signup = gtk.Button('Conectar')
        
        table = gtk.Table(8,1,False)
        table.attach(avatar,0,1,0,1,gtk.FILL,gtk.FILL, 20, 10)
        table.attach(self.message,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 3)
        table.attach(lbl_user,0,1,2,3,gtk.EXPAND,gtk.FILL,0,0)
        table.attach(self.username,0,1,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 0)
        table.attach(lbl_pass,0,1,4,5,gtk.EXPAND,gtk.FILL, 0, 5)
        table.attach(self.password,0,1,5,6,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 0)
        table.attach(self.btn_signup,0,1,7,8,gtk.EXPAND,gtk.FILL,0, 30)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(table, False, False, 2)
        
        self.add(self.vbox)
        self.show_all()
        
        self.btn_signup.connect('clicked', self.signin, self.username, self.password)
        self.password.connect('activate', self.signin, self.username, self.password)
        
    def signin(self, widget, username, password):
        self.btn_signup.set_sensitive(False)
        self.username.set_sensitive(False)
        self.password.set_sensitive(False)
        self.request_signin(username.get_text(), password.get_text())
        
    def cancel_login(self, error):
        #e = '<span background="#C00" foreground="#FFF" size="small">%s</span>' % error
        self.message.set_error(error)
        self.btn_signup.set_sensitive(True)
        self.username.set_sensitive(True)
        self.password.set_sensitive(True)
        
    def show_main(self):
        log.debug('Cargando ventana principal')
        self.mode = 2
        
        self.contentbox.add(self.contenido)
        
        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0, 'Turpial')
        if (self.vbox is not None): self.remove(self.vbox)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(self.contentbox, True, True, 0)
        self.vbox.pack_start(self.dock, False, False, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        
        self.add(self.vbox)
        self.switch_mode()
        self.show_all()
        
        gobject.timeout_add(3*60*1000, self.download_timeline)
        gobject.timeout_add(5*60*1000, self.download_rates)
        gobject.timeout_add(10*60*1000, self.download_replies)
        gobject.timeout_add(15*60*1000, self.download_directs)
        
        
    def show_home(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.home
        self.contentbox.add(self.contenido)
        
    def show_favs(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.favs
        self.contentbox.add(self.contenido)
        
    def show_profile(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.profile
        self.contentbox.add(self.contenido)
    
    def show_search(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.search
        self.contentbox.add(self.contenido)
        
    def show_update_box(self, text='', id='', user=''):
        if self.updatebox.get_property('visible'): 
            self.updatebox.present()
            return
        self.updatebox.show(text, id, user)
        
    def update_timeline(self, tweets):
        if tweets is None: return
        log.debug(u'Actualizando el timeline')
        self.home.timeline.update_tweets(tweets)
        
    def update_replies(self, tweets):
        if tweets is None: return
        log.debug(u'Actualizando las replies')
        self.home.replies.update_tweets(tweets)
        
    def update_favs(self, tweets):
        if tweets is None: return
        log.debug(u'Actualizando favoritos')
        self.favs.favorites.update_tweets(tweets)
        
    def update_directs(self, sent, recv):
        if recv is None: return
        log.debug(u'Actualizando mensajes directos')
        self.home.direct.update_tweets(sent)
        
    def update_user_profile(self, profile):
        if profile is None: return
        log.debug(u'Actualizando perfil del usuario')
        self.profile.set_user_profile(profile)
        
    def update_following(self, people):
        if people is None: return
        log.debug(u'Actualizando following')
        self.profile.set_following(people)
        
    def update_followers(self, people):
        if people is None: return
        log.debug(u'Actualizando followers')
        self.profile.set_followers(people)
        
    def update_rate_limits(self, val):
        if val is None: return
        self.statusbar.push(0, util.get_rates(val))
        
    def update_search_topics(self, val):
        if val is None: return
        self.search.topics.update_tweets(val['results'])
        
    def get_user_avatar(self, user, pic_url):
        pix = self.request_user_avatar(user, pic_url)
        if pix:
            return util.load_avatar(pix)
        else:
            return util.load_image('unknown.png', pixbuf=True)
        
    def update_user_avatar(self, user, pic):
        self.home.timeline.update_user_pic(user, pic)
        self.home.replies.update_user_pic(user, pic)
        self.home.direct.update_user_pic(user, pic)
        self.favs.favorites.update_user_pic(user, pic)
        self.profile.following.update_user_pic(user, pic)
        self.profile.followers.update_user_pic(user, pic)
        self.profile.user_form.update_user_pic(user, pic)
        self.search.topics.update_user_pic(user, pic)
        
    def switch_mode(self, widget=None):
        cur_x, cur_y = self.get_position()
        cur_w, cur_h = self.get_size()
        
        if self.workspace == 'single':
            self.workspace = 'wide'
            self.set_size_request(960, 480)
            self.resize(960, 480)
            x = (960 - cur_w)/2
            self.move(cur_x - x, cur_y)
        else:
            self.workspace = 'single'
            self.set_size_request(320, 480)
            self.resize(320, 480)
            x = (cur_w - 320)/2
            self.move(cur_x + x, cur_y)
        
        self.dock.change_mode(self.workspace)
        self.home.change_mode(self.workspace)
        self.favs.change_mode(self.workspace)
        self.search.change_mode(self.workspace)
        self.profile.change_mode(self.workspace)
        self.show_all()
        
    def size_request(self, widget, event, data=None):
        """Callback when the window changes its sizes. We use it to set the
        proper word-wrapping for the message column."""
        if self.mode < 2: return
        
        w, h = self.get_size()
        self.contenido.update_wrap(w, self.workspace)
        return
        

# -*- coding: utf-8 -*-

# Widget para mostrar tweets en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 20, 2009

import gtk
import pango
import logging
import gobject
import webbrowser

from ui import util as util

log = logging.getLogger('Gtk:TweetList')

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

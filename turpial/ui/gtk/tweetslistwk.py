# -*- coding: utf-8 -*-

# Widget para mostrar tweets en Turpial usando WebKit
#
# Author: Wil Alvarez (aka Satanas)
# Feb 16, 2010

import os
import gtk
import pango
import webkit
import gobject
import logging
import webbrowser

from turpial.ui.gtk.waiting import *
from turpial.ui import util as util

log = logging.getLogger('Gtk:Tweetlist')

gobject.threads_init()

class TweetListWebkit(gtk.VBox):
    def __init__(self, mainwin, label='', menu='normal'):
        gtk.VBox.__init__(self, False)
        
        self.last = None    # Last tweets updated
        self.mainwin = mainwin
        style_path = os.path.join(os.path.dirname(__file__), '..', '..', 
            'data', 'themes', 'default', 'style.css')
        template_path = os.path.join(os.path.dirname(__file__), '..', '..', 
            'data', 'themes', 'default', 'tweet_template.html')
        
        #self.header = '<link href="%s" rel="stylesheet" type="text/css">' % style_path
        #self.header = ''
        f = open(style_path, 'r')
        self.css_template = f.read()
        f.close()
        self.header = '<style type="text/css"> %s </style>' % self.css_template
        self.page = self.header
        f = open(template_path, 'r')
        self.tweet_template = f.read()
        f.close()
        
        self.list = webkit.WebView()
        self.settings = webkit.WebSettings()
        self.list.set_settings(self.settings)
        
        self.label = gtk.Label(label)
        self.caption = label
        
        self.lblerror = gtk.Label()
        self.lblerror.set_use_markup(True)
        self.waiting = CairoWaiting(self.mainwin)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        bottombox = gtk.HBox(False)
        bottombox.pack_start(self.lblerror, False, False, 2)
        bottombox.pack_start(align, True, True, 2)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.list)
            
        self.pack_start(scroll, True, True)
        self.pack_start(bottombox, False, False)
        
    def __highlight_hashtags(self, text):
        hashtags = util.detect_hashtags(text)
        if len(hashtags) == 0: return text
        
        for h in hashtags:
            torep = '#%s' % h
            cad = '<span foreground="#%s">#%s</span>' % (self.mainwin.link_color, h)
            text = text.replace(torep, cad)
        return text
        
    def __highlight_mentions(self, text):
        mentions = util.detect_mentions(text)
        if len(mentions) == 0: return text
        
        for h in mentions:
            if len(h) == 1: continue
            torep = '@%s' % h
            cad = '<span foreground="#%s">@%s</span>' % (self.mainwin.link_color, h)
            text = text.replace(torep, cad)
        return text
        
    def __highlight_urls(self, urls, text):
        #if len(urls) == 0: return text
        
        for u in urls:
            cad = '<span foreground="#%s">%s</span>' % (self.mainwin.link_color, u)
            text = text.replace(u, cad)
        return text
        
    def __open_url_with_event(self, widget, event, url):
        if (event.button == 1) or (event.button == 3):
            self.__open_url(widget, url)
            
    def __open_url(self, widget, url):
        log.debug('Opening url %s' % url)
        webbrowser.open(url)
        
    def __show_update_box(self, widget, text, in_reply_id='', in_reply_user=''):
        self.mainwin.show_update_box(text, in_reply_id, in_reply_user)
        
    def __retweet(self, widget, id):
        self.mainwin.request_retweet(id)
        
    def __delete(self, widget, id):
        self.mainwin.request_destroy_status(id)
    
    def __delete_direct(self, widget, id):
        self.mainwin.request_destroy_direct(id)
        
    def __fav(self, widget, fav, id):
        if fav:
            self.mainwin.request_fav(id)
        else:
            self.mainwin.request_unfav(id)
    
    def __follow(self, widget, follow, user):
        if follow:
            self.mainwin.request_follow(user)
        else:
            self.mainwin.request_unfollow(user)
        
    def __in_reply_to(self, widget, user, in_reply_to_id):
        self.mainwin.request_conversation(in_reply_to_id, user)
        
    def __mute(self, widget, user):
        self.mainwin.request_update_muted(user)
        
    def clear(self):
        self.page = self.header
                
    def update_wrap(self, val):
        pass
        
    def add_tweet(self, tweet, render=True):
        client = ''
        in_reply = ''
        retweeted = ''
        
        p = self.mainwin.parse_tweet(tweet)
        
        urls = util.detect_urls(p.text)
        html_twt = p.text
        html_twt = self.__highlight_hashtags(html_twt)
        html_twt = self.__highlight_mentions(html_twt)
        html_twt = self.__highlight_urls(urls, html_twt)
        
        if p.source: 
            client = ' %s %s' % (_('from'), p.source)
        if p.in_reply_to_user:
            in_reply = ' %s %s' % (_('in reply to'), p.in_reply_to_user)
        if p.retweet_by:
            retweeted += '%s %s' % (_('Retweeted by'), p.retweet_by)
        
        twt = self.tweet_template
        twt = twt.replace('${avatar}', p.avatar)
        twt = twt.replace('${username}', p.username)
        twt = twt.replace('${text}', html_twt)
        twt = twt.replace('${date}', p.timestamp)
        twt = twt.replace('${client}', client)
        twt = twt.replace('${in_reply_to}', in_reply)
        twt = twt.replace('${retweeted_by}', retweeted)
        
        self.page += twt
        if render: 
            gobject.idle_add(self.list.load_string, self.page, "text/html", "iso-8859-15", "timeline")
        #color = gtk.gdk.Color(255*257, 242*257, 212*257) if p['fav'] else None
        color = gtk.gdk.Color(250*257, 237*257, 187*257) if p.is_favorite else None
        
    def update_user_pic(self, user, pic):
        # Evaluar si es más eficiente esto o cargar toda la lista cada vez
        pix = self.mainwin.load_avatar(self.mainwin.imgdir, pic)
        iter = self.model.get_iter_first()
        while iter:
            u = self.model.get_value(iter, 1)
            if u == user:
                self.model.set_value(iter, 0, pix)
            iter = self.model.iter_next(iter)
        del pix
        
    def update_tweets(self, response):
        if response.type == 'error':
            self.stop_update(True, response.errmsg)
            return 0
            
        arr_tweets = response.items
        if len(arr_tweets) == 0:
            self.clear()
            self.stop_update(True, _('No tweets available'))
            return 0
        else:
            count = util.count_new_tweets(arr_tweets, self.last)
            self.stop_update()
            self.clear()
            for tweet in arr_tweets:
                if not tweet:
                    continue
                self.add_tweet(tweet, False)
            self.last = arr_tweets
            gobject.idle_add(self.list.load_string, self.page, "text/html", "utf-8", "timeline")
            return count
            
    def start_update(self):
        self.waiting.start()
        self.lblerror.set_markup("")
        
    def stop_update(self, error=False, msg=''):
        self.waiting.stop(error)
        self.lblerror.set_markup(u"<span size='small'>%s</span>" % msg)

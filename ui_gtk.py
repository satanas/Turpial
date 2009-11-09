#!/usr/bin/python
# -*- coding: utf-8 -*-

# Interfaz Gráfica Tonta para Turpial en PyGTK
#
# Author: Wil Alvarez (aka Satanas)
# Nov 08, 2009

import re
import gtk
import time
import pango

def load_image(path):
    pix = gtk.gdk.pixbuf_new_from_file(path)
    avatar = gtk.Image()
    avatar.set_from_pixbuf(pix)
    del pix
    return avatar

class TweetList(gtk.ScrolledWindow):
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        
        self.hashtag_pattern = re.compile('\#(.*?)[\W]')
        self.mention_pattern = re.compile('\@(.*?)[\W]')
        
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.add(self.list)
        self.set_shadow_type(gtk.SHADOW_IN)
        
        # avatar, username, datetime, client, message
        self.model = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str)
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
        
    def __highlight_hashtags(self, text):
        hashtags = self.hashtag_pattern.findall(text)
        if len(hashtags) == 0: return text
        
        for h in hashtags:
            torep = '#%s' % h
            cad = '<span foreground="#FF6633">#%s</span>' % h
            text = text.replace(torep, cad)
        return text
        
    def __highlight_mentions(self, text):
        mentions = self.mention_pattern.findall(text)
        if len(mentions) == 0: return text
        
        for h in mentions:
            torep = '@%s' % h
            cad = '<span foreground="#FF6633">@%s</span>' % h
            text = text.replace(torep, cad)
        return text
        
    def update_wrap(self, val):
        self.cell_tweet.set_property('wrap-width', val - 60)
        iter = self.model.get_iter_first()
        
        while iter:
            path = self.model.get_path(iter)
            self.model.row_changed(path, iter)
            iter = self.model.iter_next(iter)
        
    def add_tweet(self, username, datetime, client, message, avatar=None):
        pix = gtk.gdk.pixbuf_new_from_file('unknown.png')
        user = '<small>@%s hace %s desde <i>%s</i></small>' % (username, datetime, client)
        message = '<span size="9000">%s</span>\n%s' % (message, user)
        
        message = self.__highlight_hashtags(message)
        message = self.__highlight_mentions(message)
        
        self.model.append([pix, username, datetime, client, message])
        del pix
        
    def update_tweets(self, arr_tweets):
        for tweet in arr_tweets:
            self.add_tweet(tweet['user']['screen_name'], 'XXX', 'Cliente', tweet['text'])
        
class UpdateBox(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False, 2)
        label = gtk.Label()
        label.set_use_markup(True)
        label.set_alignment(0, 0.5)
        label.set_markup('<span size="medium"><b>What are you doing?</b></span>')
        label.set_justify(gtk.JUSTIFY_LEFT)
        
        self.num_chars = gtk.Label()
        self.num_chars.set_use_markup(True)
        self.num_chars.set_markup('<span size="14000" foreground="#999"><b>140</b></span>')
        
        frame = gtk.Frame()
        self.update_text = gtk.TextView()
        self.update_text.set_border_width(2)
        self.update_text.set_left_margin(2)
        self.update_text.set_right_margin(2)
        self.update_text.set_wrap_mode(gtk.WRAP_WORD)
        self.update_text.get_buffer().connect("changed", self.count_chars)
        frame.add(self.update_text)
        
        btn_url = gtk.Button()
        btn_url.set_image(load_image('cut.png'))
        btn_url.set_tooltip_text('Shorten URL')
        btn_pic = gtk.Button()
        btn_pic.set_image(load_image('photos.png'))
        btn_pic.set_tooltip_text('Upload Pic')
        btn_clr = gtk.Button()
        btn_clr.set_image(load_image('clear.png'))
        btn_clr.set_tooltip_text('Clear Box')
        btn_upd = gtk.Button('Update')
        
        top = gtk.HBox(False)
        top.pack_start(label, True, True, 3)
        top.pack_start(self.num_chars, False, False, 3)
        
        buttonbox = gtk.HBox(False)
        buttonbox.pack_start(btn_url, False, False, 0)
        buttonbox.pack_start(btn_pic, False, False, 0)
        buttonbox.pack_start(btn_clr, False, False, 0)
        
        vbox = gtk.VBox(False)
        vbox.pack_start(btn_upd, True, True, 0)
        vbox.pack_start(buttonbox, False, False, 0)
        
        bottom = gtk.HBox(False)
        bottom.pack_start(frame, True, True, 3)
        bottom.pack_start(vbox, False, False, 3)
        
        self.pack_start(top, False, False, 2)
        self.pack_start(bottom, True, True, 2)
        self.show_all()
    
    def count_chars(self, widget):
        buf = self.update_text.get_buffer()
        remain = 140 - buf.get_char_count()
        
        if remain >= 20: color = "#999"
        elif 0 < remain < 20: color = "#d4790d"
        else: color = "#D40D12"
        
        self.num_chars.set_markup('<span size="14000" foreground="%s"><b>%i</b></span>' % (color, remain))
        
class Main(gtk.Window):
    def __init__(self, controller):
        gtk.Window.__init__(self)
        
        self.controller = controller
        self.set_title('Turpial: 1era Prueba de concepto')
        self.set_size_request(60, 60)
        self.set_default_size(320, 480)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect('destroy', gtk.main_quit)
        self.connect('size-request', self.size_request)
        self.mode = 0
        self.vbox = None
        
    def main_loop(self):
        gtk.main()
        
    def show_login(self):
        self.mode = 1
        if self.vbox is not None: self.remove(self.vbox)
        
        self.message = gtk.Label()
        self.message.set_use_markup(True)
        self.message.set_alignment(0, 0.5)
        self.message.set_justify(gtk.JUSTIFY_LEFT)
        
        lbl_user = gtk.Label()
        lbl_user.set_justify(gtk.JUSTIFY_LEFT)
        lbl_user.set_use_markup(True)
        lbl_user.set_markup('<span background="#C00" foreground="#FFF" size="small">Username</span>')
        
        lbl_pass = gtk.Label()
        lbl_pass.set_justify(gtk.JUSTIFY_LEFT)
        lbl_pass.set_use_markup(True)
        lbl_pass.set_markup('<span size="small">Password</span>')
        
        username = gtk.Entry()
        password = gtk.Entry()
        password.set_visibility(False)
        
        self.btn_signup = gtk.Button('Conectar')
        
        
        table = gtk.Table(8,1,False)
        
        table.attach(self.message,0,1,1,2,gtk.FILL,gtk.FILL, 20, 0)
        table.attach(lbl_user,0,1,2,3,gtk.EXPAND,gtk.FILL,0,0)
        table.attach(username,0,1,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 0)
        table.attach(lbl_pass,0,1,4,5,gtk.EXPAND,gtk.FILL, 0, 5)
        table.attach(password,0,1,5,6,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 0)
        #table.attach(alignRem,0,1,6,7,gtk.EXPAND,gtk.FILL,0, 0)
        table.attach(self.btn_signup,0,1,7,8,gtk.EXPAND,gtk.FILL,0, 30)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(table, False, False, 2)
        
        self.add(self.vbox)
        self.show_all()
        
        self.btn_signup.connect('clicked', self.request_login, username, password)
        
    def request_login(self, widget, username, password):
        self.btn_signup.set_sensitive(False)
        gtk.main_iteration(False)
        self.controller.signup(username.get_text(), password.get_text())
        
    def cancel_login(self, error):
        e = '<span background="#C00" foreground="#FFF" size="small">%s</span>' % error
        self.message.set_markup(e)
        self.btn_signup.set_sensitive(True)
        
    def update_rate_limits(self, val):
        t = time.strftime('%H:%M:%S', time.gmtime(val['reset_time_in_seconds']))
        hits = val['remaining_hits']
        limit = val['hourly_limit']
        status = "%s/%s API calls remain. Next reset at %s" % (hits, limit, t)
        self.statusbar.push(0, status)
        
    def show_main(self):
        self.mode = 2
        self.timeline = TweetList()
        self.replies = TweetList()
        self.direct = TweetList()
        self.favorites = TweetList()
        
        self.updatebox = UpdateBox()
        
        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0, '103 API calls remain. Next reset: 08:05 pm')
        
        self.notebook = gtk.Notebook()
        self.notebook.append_page(self.timeline, gtk.Label('Home'))
        self.notebook.append_page(self.replies, gtk.Label('Replies'))
        self.notebook.append_page(self.direct, gtk.Label('Messages'))
        self.notebook.append_page(self.favorites, gtk.Label('Favorites'))
        
        if (self.vbox is not None): self.remove(self.vbox)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(self.notebook, True, True, 0)
        self.vbox.pack_start(self.updatebox, False, False, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        
        self.add(self.vbox)
        self.show_all()
            
    def size_request(self, widget, event, data=None):
        """Callback when the window changes its sizes. We use it to set the
        proper word-wrapping for the message column."""
        if self.mode < 2:  return
        
        w, h = self.get_size()
        self.timeline.update_wrap(w)
        self.replies.update_wrap(w)
        self.direct.update_wrap(w)
        self.favorites.update_wrap(w)
        return
'''
p.timeline.add_tweet('usuario', '00:00:00', 'Mitter', 
    'Mi primera lista se llamara: quiero que me pegues una gripe, una que nos deje en cama por semanas corridas. jajajajajajajaja')
p.timeline.add_tweet('pedroperez', '00:00:00', 'Cliente2', 
    'Probando un tweet normalongo... Dummy')
p.timeline.add_tweet('satanas', '00:00:00', 'Otroahi', 
    'Hell yeah!!!')
p.timeline.add_tweet('satanas', '00:00:00', 'Otroahi', 
    'Probando #hashtags, #probando... #probando!!!')
p.timeline.add_tweet('satanas', '00:00:00', 'Otroahi', 
    'Probando @menciones, @meeencionesss, @mentadas... @coladas!!! la @tuya por sia')

p.replies.add_tweet('xxx', '00:00:00', 'web',
    '@satanas Interesting: Collecting Headlines Funnier Than This http://ff.im/-aVIFW')

p.direct.add_tweet('xxx', '00:00:00', 'web',
    'Could, would, should, might, maybe, ought to, perhaps. These words do not exist in Agile')
'''

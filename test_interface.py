#!/usr/bin/python

# Primera aproximacion de Turpial usando solo PyGTK
#
# Author: Wil Alvarez (aka Satanas)
# Oct 28, 2009

import re
import gtk
import pango


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
        
class UpdateBox(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False, 2)
        chat = gtk.Label()
        chat.set_use_markup(True)
        chat.set_alignment(0, 0.5)
        chat.set_markup('<span size="medium"><b>What are you doing?</b></span>')
        chat.set_justify(gtk.JUSTIFY_LEFT)
        
        self.num_chars = gtk.Label()
        self.num_chars.set_use_markup(True)
        self.num_chars.set_markup('<span size="14000" foreground="#999"><b>140</b></span>')
        
        self.update_text = gtk.TextView()
        self.update_text.set_border_width(1)
        self.update_text.set_wrap_mode(gtk.WRAP_WORD)
        self.update_text.get_buffer().connect("changed", self.count_chars)
        
        btn_url = gtk.Button('url')
        btn_pic = gtk.Button('pic')
        btn_upd = gtk.Button('Update')
        
        top = gtk.HBox(False)
        top.pack_start(chat, True, True, 3)
        top.pack_start(self.num_chars, False, False, 3)
        
        middle = gtk.HBox(False)
        middle.pack_start(self.update_text, True, True, 3)
        
        buttonbox = gtk.HButtonBox()
        middle.pack_start(btn_upd, False, False, 2)
        buttonbox.pack_start(btn_url, False, False, 2)
        buttonbox.pack_start(btn_pic, False, False, 2)
        
        self.pack_start(top, False, False, 2)
        self.pack_start(middle, True, True, 2)
        #self.pack_start(buttonbox, True, True, 2)
        self.show_all()
    
    def count_chars(self, widget):
        buf = self.update_text.get_buffer()
        remain = 140 - buf.get_char_count()
        
        if remain >= 20: color = "#999"
        elif 0 < remain < 20: color = "#d4790d"
        else: color = "#D40D12"
        
        self.num_chars.set_markup('<span size="14000" foreground="%s"><b>%i</b></span>' % (color, remain))
        
class Prueba(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title('Turpial: 1era Prueba de concepto')
        self.set_size_request(60, 60)
        self.set_default_size(320, 600)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect('destroy', gtk.main_quit)
        self.connect('size-request', self.size_request)
        
        self.timeline = TweetList()
        self.replies = TweetList()
        self.direct = TweetList()
        self.favorites = TweetList()
        
        self.updatebox = UpdateBox()
        
        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0, '103/150 API calls. Next reset: 08:05 pm')
        
        self.notebook = gtk.Notebook()
        self.notebook.append_page(self.timeline, gtk.Label('Home'))
        self.notebook.append_page(self.replies, gtk.Label('Replies'))
        self.notebook.append_page(self.direct, gtk.Label('Messages'))
        self.notebook.append_page(self.favorites, gtk.Label('Favorites'))
        
        vbox = gtk.VBox(False, 5)
        vbox.pack_start(self.notebook, True, True, 0)
        vbox.pack_start(self.updatebox, False, False, 0)
        vbox.pack_start(self.statusbar, False, False, 0)
        
        self.add(vbox)
        self.show_all()
        
        self.timeline.add_tweet('usuario', '00:00:00', 'Mitter', 
            'Mi primera lista se llamara: quiero que me pegues una gripe, una que nos deje en cama por semanas corridas. jajajajajajajaja')
        self.timeline.add_tweet('pedroperez', '00:00:00', 'Cliente2', 
            'Probando un tweet normalongo... Dummy')
        self.timeline.add_tweet('satanas', '00:00:00', 'Otroahi', 
            'Hell yeah!!!')
        self.timeline.add_tweet('satanas', '00:00:00', 'Otroahi', 
            'Probando #hashtags, #probando... #probando!!!')
        self.timeline.add_tweet('satanas', '00:00:00', 'Otroahi', 
            'Probando @menciones, @meeencionesss, @mentadas... @coladas!!! la @tuya por sia')
        
    def size_request(self, widget, event, data=None):
        """Callback when the window changes its sizes. We use it to set the
        proper word-wrapping for the message column."""
        
        w, h = self.get_size()
        self.timeline.update_wrap(w)
        return
    
Prueba()
gtk.main()

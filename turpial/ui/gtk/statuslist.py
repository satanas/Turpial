# -*- coding: utf-8 -*-

# Widget para mostrar estados en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 25, 2009

import gtk
import pango
import gobject
import logging

from turpial.ui import util as util
from turpial.ui.gtk.menu import Menu

log = logging.getLogger('Gtk:Statuslist')

OFFENSE_CHARS = {
    'ü': 'u',
    'Ü': 'U',
}

class StatusList(gtk.ScrolledWindow):
    def __init__(self, mainwin, mark_new=False):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        
        self.last = None    # Last tweets updated
        self.mainwin = mainwin
        self.mark_new = mark_new
        self.autoscroll = True
        self.popup_menu = Menu(mainwin)
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        #self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        
        self.model = gtk.ListStore(
            gtk.gdk.Pixbuf, # avatar
            str, # username
            str, # datetime
            str, # client
            str, # pango_message
            str, # real_message
            str, # id
            bool, # favorited?
            gobject.TYPE_PYOBJECT, # in_reply_to_id
            gobject.TYPE_PYOBJECT, # in_reply_to_user
            gobject.TYPE_PYOBJECT, # retweeted_by
            gtk.gdk.Color, # color
            str, # update type
            str, # protocol
            bool, # own tweet?
        )
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
        column.set_attributes(self.cell_tweet, markup=4, cell_background_gdk=11)
        column.set_attributes(cell_avatar, pixbuf=0, cell_background_gdk=11)
        self.list.append_column(column)
        self.list.connect("button-release-event", self.__popup_menu)
            
        self.add(self.list)
        
    def __highlight_hashtags(self, text):
        hashtags = util.detect_hashtags(text)
        if len(hashtags) == 0: return text
        
        for h in hashtags:
            torep = '%s' % h
            try:
                cad = '<span foreground="%s">%s</span>' % \
                    (self.mainwin.link_color, h)
                text = text.replace(torep, cad)
            except:
                log.debug('Problemas para resaltar el hashtag: %s' % h)
        return text
        
    def __highlight_groups(self, text):
        if not self.mainwin.request_groups_url(): 
            return text
        
        groups = util.detect_groups(text)
        if len(groups) == 0: return text
        
        for h in groups:
            torep = '%s' % h
            try:
                cad = '<span foreground="%s">%s</span>' % \
                    (self.mainwin.link_color, h)
                text = text.replace(torep, cad)
            except:
                log.debug('Problemas para resaltar el grupo: %s' % h)
        return text
        
    def __highlight_mentions(self, text):
        mentions = util.detect_mentions(text)
        if len(mentions) == 0:
            return text
        
        for h in mentions:
            if len(h) == 1: 
                continue
            torep = '%s' % h
            cad = '<span foreground="%s">%s</span>' % \
                  (self.mainwin.link_color, h)
            text = text.replace(torep, cad)
        return text
        
    def __highlight_urls(self, urls, text):
        #if len(urls) == 0: return text
        
        for u in urls:
            cad = '<span foreground="%s">%s</span>' % \
                  (self.mainwin.link_color, u)
            text = text.replace(u, cad)
        return text
        
    def __popup_menu(self, widget, event):
        model, row = widget.get_selection().get_selected()
        if (row is None):
            return False
        
        if (event.button == 3):
            user = model.get_value(row, 1)
            msg = model.get_value(row, 5)
            uid = model.get_value(row, 6)
            in_reply_to_id = model.get_value(row, 8)
            utype = model.get_value(row, 12)
            protocol = model.get_value(row, 13)
            own = model.get_value(row, 14)
                
            menu = self.popup_menu.build(uid, user, msg, in_reply_to_id, utype, 
                protocol, own)
            menu.show_all()
            menu.popup(None, None, None, event.button , event.time)
    
    def clear(self):
        self.model.clear()
        
    def update_wrap(self, val):
        self.cell_tweet.set_property('wrap-width', val - 85)
        iter = self.model.get_iter_first()
        
        while iter:
            path = self.model.get_path(iter)
            self.model.row_changed(path, iter)
            iter = self.model.iter_next(iter)
        
    def add_tweet(self, tweet, insert=True):
        p = self.mainwin.parse_tweet(tweet)
        pix = self.mainwin.get_user_avatar(p.username, p.avatar)
        
        # Detect invalid chars that offend pango
        for inv_chr in OFFENSE_CHARS:
            if p.text.find(inv_chr) >= 0:
                p.text = p.text.replace(inv_chr, OFFENSE_CHARS[inv_chr])
        
        urls = [gobject.markup_escape_text(u) \
                for u in util.detect_urls(p.text)]
        
        pango_twt = util.unescape_text(p.text)
        pango_twt = gobject.markup_escape_text(pango_twt)
        
        user = '<span size="9000" foreground="%s"><b>%s</b></span> ' % \
            (self.mainwin.link_color, p.username)
        pango_twt = '<span size="9000">%s</span>' % pango_twt
        pango_twt = self.__highlight_hashtags(pango_twt)
        pango_twt = self.__highlight_groups(pango_twt)
        pango_twt = self.__highlight_mentions(pango_twt)
        pango_twt = self.__highlight_urls(urls, pango_twt)
        pango_twt += '<span size="2000">\n\n</span>'
        try:
            pango_twt = user + pango_twt
        except UnicodeDecodeError:
            print pango_twt
            print user            
        
        footer = '<span size="small" foreground="#999">%s' % p.timestamp
        if p.source: 
            footer += ' %s %s' % (_('from'), p.source)
        if p.in_reply_to_user:
            footer += ' %s %s' % (_('in reply to'), p.in_reply_to_user)
        if p.retweet_by:
            footer += '\n%s %s' % (_('Retweeted by'), p.retweet_by)
        footer += '</span>'
        
        pango_twt += footer
        
        #naranja = gtk.gdk.Color(250 * 257, 241 * 257, 205 * 257)
        #amarillo = gtk.gdk.Color(255 * 257, 251 * 257, 230 * 257)
        #verde = gtk.gdk.Color(233 * 257, 247 * 257, 233 * 257)
        #azul = gtk.gdk.Color(235 * 257, 242 * 257, 255 * 257)
        
        msg = p.text.lower()
        me = '@'+self.mainwin.me
        mention = True if msg.find(me.lower()) >= 0 else False
        own = True if p.username.lower() == self.mainwin.me.lower() else False
        
        if p.is_favorite:
            color = gtk.gdk.Color(250 * 257, 241 * 257, 205 * 257)
        elif own:
            color = gtk.gdk.Color(255 * 257, 229 * 257, 229 * 257)
        elif mention:
            color = gtk.gdk.Color(233 * 257, 247 * 257, 233 * 257)
        #elif self.mark_new:
        #    color = gtk.gdk.Color(235 * 257, 242 * 257, 255 * 257)
        else:
            color = None
            
        row = [pix, p.username, p.datetime, p.source, pango_twt, p.text, p.id, 
            p.is_favorite, p.in_reply_to_id, p.in_reply_to_user, p.retweet_by, 
            color, p.type, p.protocol, own]
        
        if insert:
            self.model.insert(0, row)
        else:
            self.model.append(row)
        
        if not self.autoscroll:
            model, row = self.list.get_selection().get_selected()
            if row:
                path = self.model.get_path(row)
                if path[0] <= 1:
                    self.list.get_selection().select_path((0,))
                    self.list.set_cursor((0,))
            else:
                self.list.get_selection().select_path((0,))
                self.list.set_cursor((0,))
        
        del pix
        
    def del_last(self):
        last = self.model.iter_n_children(None)
        print 'Last:', last
        iter = self.model.get_iter_from_string(str(last - 1))
        #iter = self.model.get_iter_from_string('0')
        print 'Borrando último tweet:', self.model.get_value(iter, 5)
        self.model.remove(iter)
        
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
        
    def set_autoscroll(self, value):
        self.autoscroll = value
        
    '''
    def unset_bg_color(self):
        print "unset_bg_color"
        iter = self.model.get_iter_first()
        while iter:
            color = self.model.get_value(iter, 11)
            fav = self.model.get_value(iter, 7)
            if not fav: 
                if color:
                    self.model.set_value(iter, 11, None)
            iter = self.model.iter_next(iter)
    '''

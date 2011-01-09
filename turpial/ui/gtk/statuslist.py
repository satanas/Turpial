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

FIELDS = 16

class StatusList(gtk.ScrolledWindow):
    def __init__(self, mainwin):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        
        self.last = None    # Last tweets updated
        self.mainwin = mainwin
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
            bool, # own status?
            bool, # new status?
            str, #timestamp original
        ) # Editar FIELDS
        
        self.model.set_sort_column_id(16, gtk.SORT_DESCENDING)
        self.list.set_model(self.model)
        cell_avatar = gtk.CellRendererPixbuf()
        cell_avatar.set_property('yalign', 0)
        self.cell_tweet = gtk.CellRendererText()
        self.cell_tweet.set_property('wrap-mode', pango.WRAP_WORD_CHAR)
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
        self.list.connect("button-release-event", self.__on_click)
        self.click_handler = self.list.connect("cursor-changed", self.__on_select)
            
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
        
    def __on_select(self, widget):
        model, row = widget.get_selection().get_selected()
        if (row is None):
            return False
        
        if model.get_value(row, 15):
            path = model.get_path(row)
            self.__mark_as_read(model, path, row)
    
    def __on_click(self, widget, event):
        model, row = widget.get_selection().get_selected()
        if (row is None):
            return False
        
        if (event.button == 3):
            self.__popup_menu(model, row, event)
        
    def __popup_menu(self, model, row, event):
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
    
    def __get_background_color(self, fav, own, msg, new):
        ''' Returns the bg color for an update according it status '''
        #naranja = gtk.gdk.Color(250 * 257, 241 * 257, 205 * 257)
        #amarillo = gtk.gdk.Color(255 * 257, 251 * 257, 230 * 257)
        #verde = gtk.gdk.Color(233 * 257, 247 * 257, 233 * 257)
        #azul = gtk.gdk.Color(235 * 257, 242 * 257, 255 * 257)
        
        azul = gtk.gdk.Color(229 * 257, 236 * 257, 255 * 257)
        rojo = gtk.gdk.Color(255 * 257, 229 * 257, 229 * 257)
        morado = gtk.gdk.Color(238 * 257, 229 * 257, 255 * 257)
        cyan = gtk.gdk.Color(229 * 257, 255 * 257, 253 * 257)
        verde = gtk.gdk.Color(229 * 257, 255 * 257, 230 * 257)
        amarillo = gtk.gdk.Color(253 * 257, 255 * 257, 229 * 257)
        naranja = gtk.gdk.Color(255 * 257, 240 * 257, 229 * 257)
        
        me = '@'+self.mainwin.me.lower()
        mention = True if msg.lower().find(me) >= 0 else False
        
        if new:
            color = azul
        elif fav:
            color = naranja
        elif own:
            color = rojo
        elif mention:
            color = verde
        else:
            color = None
            
        return color

    def __build_pango_text(self, status):
        ''' Transform the regular text into pango markup '''
        urls = [gobject.markup_escape_text(u) \
                for u in util.detect_urls(status.text)]
        
        pango_twt = util.unescape_text(status.text)
        pango_twt = gobject.markup_escape_text(pango_twt)
        
        user = '<span size="9000" foreground="%s"><b>%s</b></span> ' % \
            (self.mainwin.link_color, status.username)
        pango_twt = '<span size="9000">%s</span>' % pango_twt
        pango_twt = self.__highlight_hashtags(pango_twt)
        pango_twt = self.__highlight_groups(pango_twt)
        pango_twt = self.__highlight_mentions(pango_twt)
        pango_twt = self.__highlight_urls(urls, pango_twt)
        pango_twt += '<span size="2000">\n\n</span>'
        
        try:
            pango_twt = user + pango_twt
        except UnicodeDecodeError:
            clear_txt = ''
            invalid_chars = []
            for c in pango_twt:
                try:
                    clear_txt += c.encode('ascii')
                except UnicodeDecodeError:
                    invalid_chars.append(c)
                    clear_txt += '?'
            log.debug('Problema con caracteres inválidos en un tweet: %s' % invalid_chars)
            pango_twt = clear_txt
        
        footer = '<span size="small" foreground="#999">%s' % status.datetime
        if status.source: 
            footer += ' %s %s' % (_('from'), status.source)
        if status.in_reply_to_user:
            footer += ' %s %s' % (_('in reply to'), status.in_reply_to_user)
        if status.retweet_by:
            footer += '\n%s %s' % (_('Retweeted by'), status.retweet_by)
        footer += '</span>'
        pango_twt += footer
        
        return pango_twt
        
    def __update_pic(self, model, path, iter, args):
        user, pic = args
        username = model.get_value(iter, 1)
        if username == user:
            model.set_value(iter, 0, pic)
            return True
        return False
        
    def __build_iter_status(self, status, new=False):
        p = self.mainwin.parse_tweet(status)
        
        pix = self.mainwin.get_user_avatar(p.username, p.avatar)
        pango_text = self.__build_pango_text(p)
        color = self.__get_background_color(p.is_favorite, p.is_own, p.text, new)
        
        row = [pix, p.username, p.datetime, p.source, pango_text, p.text, p.id, 
            p.is_favorite, p.in_reply_to_id, p.in_reply_to_user, p.retweet_by, 
            color, p.type, p.protocol, p.is_own, new, p.timestamp]
        
        del pix
        return row
    
    def __remove_statuses(self, value):
        for i in range(value):
            last = self.model.iter_n_children(None)
            iter = self.model.get_iter_from_string(str(last - 1))
            self.model.remove(iter)
    
    def __add_statuses(self, statuses):
        ''' Append statuses to list'''
        for status in statuses:
            row = self.__build_iter_status(status)
            self.model.append(row)
            
    def __modify_statuses(self, statuses):
        inserted = 0
        new_count = 0
        current = []
        received = []
        to_del = []
        
        iter = self.model.get_iter_first()
        while iter:
            current.append(self.model.get_value(iter, 6))
            iter = self.model.iter_next(iter)
        
        for status in statuses:
            received.append(status.id)
            if status.id not in current:
                new = False
                inserted += 1
                if status.timestamp > self.last_time and status.username != self.mainwin.me:
                    new = True
                    new_count += 1
                row = self.__build_iter_status(status, new=new)
                self.model.append(row)
        
        if len(current) > len(received):
            iter = self.model.get_iter_first()
            while iter:
                if self.model.get_value(iter, 6) not in received:
                    to_del.append(iter)
                iter = self.model.iter_next(iter)
            
            for iter in to_del:
                self.model.remove(iter)
        elif len(current) == len(received):
            self.__remove_statuses(inserted)
        
        return new_count
        
    def __set_last_time(self):
        self.last_time = None
        if not self.last:
            return
        
        for status in self.last:
            if status.username != self.mainwin.me:
                self.last_time = status.timestamp
                break
    
    def __mark_as_read(self, model, path, iter):
        msg = model.get_value(iter, 5)
        fav = model.get_value(iter, 7)
        own = model.get_value(iter, 14)
        color = self.__get_background_color(fav, own, msg, False)
        model.set_value(iter, 11, color)
        model.set_value(iter, 15, False)
        
    def clear(self):
        self.model.clear()
        
    def update_wrap(self, val):
        self.cell_tweet.set_property('wrap-width', val - 85)
        iter = self.model.get_iter_first()
        while iter:
            path = self.model.get_path(iter)
            self.model.row_changed(path, iter)
            iter = self.model.iter_next(iter)
    
    def update(self, statuses):
        self.list.disconnect(self.click_handler)
        
        self.__set_last_time()
        
        new_count = 0
        if len(self.model) == 0:
            self.__add_statuses(statuses)
        else:
            new_count = self.__modify_statuses(statuses)
        
        if self.get_vadjustment().get_value() == 0.0:
            self.list.scroll_to_cell((0,))
        
        self.last = statuses
        #self.click_handler = self.list.connect("button-release-event", self.__on_click)
        self.click_handler = self.list.connect("cursor-changed", self.__on_select)
        return new_count
    
    def update_user_pic(self, user, pic):
        pix = self.mainwin.load_avatar(self.mainwin.imgdir, pic)
        self.model.foreach(self.__update_pic, (user, pix))
        del pix
        
    def mark_all_as_read(self):
        self.model.foreach(self.__mark_as_read)
        

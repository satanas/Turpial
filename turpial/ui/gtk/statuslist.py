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
from turpial.ui.gtk.follow import Follow

log = logging.getLogger('Gtk:Statuslist')

class StatusList(gtk.ScrolledWindow):
    def __init__(self, mainwin, menu='normal', mark_new=False):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(gtk.SHADOW_IN)
        
        self.last = None    # Last tweets updated
        self.mainwin = mainwin
        self.mark_new = mark_new
        self.autoscroll = True
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        #self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        
        self.model = gtk.ListStore(
            gtk.gdk.Pixbuf, # avatar
            str, #username
            str, #datetime
            str, #client
            str, #pango_message
            str, #real_message
            str, # id
            bool, #favorited?
            gobject.TYPE_PYOBJECT, # in_reply_to_id
            gobject.TYPE_PYOBJECT, # in_reply_to_user
            gobject.TYPE_PYOBJECT, # retweeted_by
            gtk.gdk.Color, #gobject.TYPE_PYOBJECT, #color
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
        
        if menu == 'normal':
            self.list.connect("button-release-event", self.__popup_menu)
        elif menu == 'direct':
            self.list.connect("button-release-event", self.__direct_popup_menu)
            
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
        
    def __build_open_menu(self, user, msg):
        _open = gtk.MenuItem(_('Open'))
        
        open_menu = gtk.Menu()
        
        total_urls = util.detect_urls(msg)
        total_users = util.detect_mentions(msg)
        total_tags = util.detect_hashtags(msg)
        total_groups = util.detect_groups(msg)
        
        if not self.mainwin.request_groups_url(): 
            total_groups = []
        
        for u in total_urls:
            url = u if len(u) < 30 else u[:30] + '...'
            umenu = gtk.MenuItem(url)
            umenu.connect('button-release-event', self.__open_url_with_event, u)
            open_menu.append(umenu)
        
        if len(total_urls) > 0 and len(total_tags) > 0: 
            open_menu.append(gtk.SeparatorMenuItem())
        
        for h in total_tags:
            hashtag = '/'.join([self.mainwin.request_hashtags_url(), h[1:]]) 
            hmenu = gtk.MenuItem(h)
            hmenu.connect('button-release-event',
                          self.__open_url_with_event, hashtag)
            open_menu.append(hmenu)
            
        for h in total_groups:
            hashtag = '/'.join([self.mainwin.request_groups_url(), h[1:]]) 
            hmenu = gtk.MenuItem(h)
            hmenu.connect('button-release-event',
                          self.__open_url_with_event, hashtag)
            open_menu.append(hmenu)
            
        if (len(total_urls) > 0 or len(total_tags) > 0 or 
            len(total_groups) > 0) and len(total_users) > 0: 
            open_menu.append(gtk.SeparatorMenuItem())
        
        exist = []
        for m in total_users:
            if m == user or m in exist:
                continue
            exist.append(m)
            user_prof = '/'.join([self.mainwin.request_profiles_url(), m[1:]])
            mentmenu = gtk.MenuItem(m)
            mentmenu.connect('button-release-event', self.__open_url_with_event, user_prof)
            open_menu.append(mentmenu)
            
        _open.set_submenu(open_menu)
        if (len(total_urls) > 0) or (len(total_users) > 0) or \
           (len(total_tags) > 0) or (len(total_groups) > 0):
            return _open
        else:
            return None
        
    def __direct_popup_menu(self, widget, event):
        model, row = widget.get_selection().get_selected()
        if (row is None):
            return False
        
        if (event.button == 3):
            user = model.get_value(row, 1)
            msg = model.get_value(row, 5)
            id = model.get_value(row, 6)
            #in_reply_to_id = model.get_value(row, 8)
             
            menu = gtk.Menu()
            rtn = self.mainwin.request_popup_info(id, user)
            
            if rtn.has_key('busy'):
                busymenu = gtk.MenuItem(rtn['busy'])
                busymenu.set_sensitive(False)
                menu.append(busymenu)
            else:
                dm = "D @%s " % user
                
                reply = gtk.MenuItem(_('Reply'))
                delete = gtk.MenuItem(_('Delete'))
                usermenu = gtk.MenuItem('@' + user)
                _open = self.__build_open_menu(user, msg)
                
                if not rtn['own']:
                    menu.append(reply)
                
                menu.append(delete)
                
                if _open:
                    menu.append(_open)
                
                menu.append(gtk.SeparatorMenuItem())
                menu.append(usermenu)
                
                user_profile = '/'.join(['http://www.twitter.com', user])
                usermenu.connect('activate', self.__open_url, user_profile)
                reply.connect('activate', self.__show_update_box, dm)
                delete.connect('activate', self.__delete_direct, id)
                
                menu.show_all()
                menu.popup(None, None, None, event.button , event.time)
        
    def __popup_menu(self, widget, event):
        model, row = widget.get_selection().get_selected()
        if (row is None):
            return False
        
        if (event.button == 3):
            user = model.get_value(row, 1)
            msg = model.get_value(row, 5)
            id = model.get_value(row, 6)
            in_reply_to_id = model.get_value(row, 8)
             
            menu = gtk.Menu()
            
            rtn = self.mainwin.request_popup_info(id, user)
            
            if rtn.has_key('busy'):
                busymenu = gtk.MenuItem(rtn['busy'])
                busymenu.set_sensitive(False)
                menu.append(busymenu)
            else:
                re = "@%s " % user
                rt = "RT @%s %s" % (user, msg)
                dm = "D @%s " % user
                
                re_all, mentions = util.get_reply_all(re, self.mainwin.me, msg)
                
                reply = gtk.MenuItem(_('Reply'))
                reply_all = gtk.MenuItem(_('Reply All'))
                retweet_old = gtk.MenuItem(_('Retweet (Old)'))
                retweet = gtk.MenuItem(_('Retweet'))
                save = gtk.MenuItem(_('+ Fav'))
                unsave = gtk.MenuItem(_('- Fav'))
                delete = gtk.MenuItem(_('Delete'))
                direct = gtk.MenuItem(_('DM'))
                follow = gtk.MenuItem(_('Follow'))
                unfollow = gtk.MenuItem(_('Unfollow'))
                loading = gtk.MenuItem(_('Loading friends...'))
                loading.set_sensitive(False)
                usermenu = gtk.MenuItem('@' + user)
                inreplymenu = gtk.MenuItem(_('In reply to'))
                mutemenu = gtk.MenuItem(_('Mute'))
                
                _open = self.__build_open_menu(user, msg)
                
                if not rtn['own']:
                    menu.append(reply)
                    if mentions > 0:
                        menu.append(reply_all)
                    menu.append(retweet_old)
                    menu.append(retweet)
                    menu.append(direct)
                    
                    if not rtn.has_key('friend'):
                        item = loading
                    elif rtn['friend'] is True:
                        item = unfollow
                    elif rtn['friend'] is False:
                        item = follow
                else:
                    menu.append(delete)
                    
                if rtn['fav']:
                    menu.append(unsave)
                else:
                    menu.append(save)
                    
                if _open:
                    menu.append(_open)
                
                if in_reply_to_id:
                    menu.append(inreplymenu)
                
                menu.append(gtk.SeparatorMenuItem())
                menu.append(usermenu)
                if not rtn['own']: 
                    if item != loading and item != follow:
                        menu.append(mutemenu)
                    menu.append(item)
                
                user_profile = '/'.join([self.mainwin.request_profiles_url(), 
                    user])
                usermenu.connect('activate', self.__open_url, user_profile)
                reply.connect('activate', self.__show_update_box, re, id, user)
                reply_all.connect('activate', self.__show_update_box, re_all, 
                    id, user)
                retweet_old.connect('activate', self.__show_update_box, rt)
                retweet.connect('activate', self.__retweet, id)
                direct.connect('activate', self.__show_update_box, dm)
                save.connect('activate', self.__fav, True, id)
                unsave.connect('activate', self.__fav, False, id)
                delete.connect('activate', self.__delete, id)
                follow.connect('activate', self.__follow, True, user)
                unfollow.connect('activate', self.__follow, False, user)
                inreplymenu.connect('activate', self.__in_reply_to,
                                    user, in_reply_to_id)
                mutemenu.connect('activate', self.__mute, user)
            
            menu.show_all()
            menu.popup(None, None, None, event.button , event.time)
        
    def __open_url_with_event(self, widget, event, url):
        if (event.button == 1) or (event.button == 3):
            self.__open_url(widget, url)
            
    def __open_url(self, widget, url):
        self.mainwin.open_url(url)
        
    def __show_update_box(self, widget, text, in_reply_id='', in_reply_user=''):
        self.mainwin.show_update_box(text, in_reply_id, in_reply_user)
        
    def __retweet(self, widget, id):
        self.mainwin.request_repeat(id)
        
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
            f = Follow(self.mainwin, user)
        else:
            self.mainwin.request_unfollow(user)
        
    def __in_reply_to(self, widget, user, in_reply_to_id):
        self.mainwin.request_conversation(in_reply_to_id, user)
        
    def __mute(self, widget, user):
        self.mainwin.request_update_muted(user)
    
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
        pango_twt = user + pango_twt
        
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
        
        mention = True if pango_twt.find('@'+self.mainwin.me) >= 0 else False
        if p.is_favorite:
            color = gtk.gdk.Color(250 * 257, 241 * 257, 205 * 257)
        elif mention:
            color = gtk.gdk.Color(233 * 257, 247 * 257, 233 * 257)
        #elif self.mark_new:
        #    color = gtk.gdk.Color(235 * 257, 242 * 257, 255 * 257)
        else:
            color = None
            
        row = [pix, p.username, p.datetime, p.source, pango_twt, p.text, p.id, 
            p.is_favorite, p.in_reply_to_id, p.in_reply_to_user, p.retweet_by, 
            color]
        
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

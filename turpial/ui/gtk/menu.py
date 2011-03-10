# -*- coding: utf-8 -*-

# Widget para construir los menús en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 27, 2010

import gtk

from turpial.ui import util as util
from turpial.ui.gtk.follow import Follow
from turpial.config import PROTOCOLS
from turpial.config import UPDATE_TYPE_DM, UPDATE_TYPE_STD, UPDATE_TYPE_PROFILE

class Menu:
    def __init__(self, mainwin):
        self.mainwin = mainwin
    
    def __request_popup_info(self, uid, user):
        return self.mainwin.request_popup_info(uid, user)
        
    # ===================================================================
    # Callbacks
    # ===================================================================
    
    def __open_url_with_event(self, widget, event, url):
        if (event.button == 1) or (event.button == 3):
            self.__open_url(widget, url)
            
    def __open_url(self, widget, url):
        self.mainwin.open_url(url)
        
    def __update_box(self, widget, text, in_reply_id='', in_reply_user=''):
        self.mainwin.show_update_box(text, in_reply_id, in_reply_user)
        
    def __retweet(self, widget, uid):
        self.mainwin.request_repeat(uid)
        
    def __delete(self, widget, uid):
        self.mainwin.request_destroy_status(uid)
    
    def __delete_direct(self, widget, uid):
        self.mainwin.request_destroy_direct(uid)
        
    def __fav(self, widget, fav, uid):
        if fav:
            self.mainwin.request_fav(uid)
        else:
            self.mainwin.request_unfav(uid)
    
    def __follow(self, widget, follow, user):
        if follow:
            f = Follow(self.mainwin, user)
        else:
            self.mainwin.request_unfollow(user)
        
    def __in_reply_to(self, widget, user, in_reply_to_id):
        self.mainwin.request_conversation(in_reply_to_id, user)
        
    def __mute(self, widget, user):
        self.mainwin.request_mute(user)
        
    # ===================================================================
    # Menu items
    # ===================================================================
    def __build_separator(self, menu):
        menu.append(gtk.SeparatorMenuItem())
        return menu
    
    def __build_busy_item(self, menu, title):
        busymenu = gtk.MenuItem(title)
        busymenu.set_sensitive(False)
        menu.append(busymenu)
        return menu
    
    def __build_reply_item(self, menu, info):
        if not info['own']:
            re_one = "@%s " % info['user']
            re_all, mentions = util.get_reply_all(re_one, self.mainwin.me, info['msg'])
            
            reply = gtk.MenuItem(_('Reply'))
            reply.connect('activate', self.__update_box, re_one, info['uid'], info['user'])
            menu.append(reply)
            if mentions > 0:
                reply_all = gtk.MenuItem(_('Reply All'))
                reply_all.connect('activate', self.__update_box, re_all, info['uid'], info['user'])
                menu.append(reply_all)
        return menu
        
    def __build_reply_dm_item(self, menu, info):
        if not info['own']:
            dm = "D @%s " % info['user']
            reply = gtk.MenuItem(_('Reply'))
            reply.connect('activate', self.__update_box, dm)
            menu.append(reply)
        return menu
    
    def __build_repeat_item(self, menu, info):
        if not info['own']:
            if info['protocol'] == PROTOCOLS[0]:
                rt = "RT @%s %s" % (info['user'], info['msg'])
                retweet_old = gtk.MenuItem(_('Retweet (Old)'))
                retweet = gtk.MenuItem(_('Retweet'))
            elif info['protocol'] == PROTOCOLS[1]:
                rt = "RD @%s %s" % (info['user'], info['msg'])
                retweet_old = gtk.MenuItem(_('Redent (Old)'))
                retweet = gtk.MenuItem(_('Redent'))
            
            retweet_old.connect('activate', self.__update_box, rt)
            retweet.connect('activate', self.__retweet, info['uid'])
            menu.append(retweet_old)
            menu.append(retweet)
        return menu
        
    def __build_direct_item(self, menu, info):
        if not info['own']:
            dm = "D @%s " % info['user']
            direct = gtk.MenuItem(_('DM'))
            direct.connect('activate', self.__update_box, dm)
            menu.append(direct)
        return menu
        
    def __build_delete_item(self, menu, info):
        if info['own']:
            delete = gtk.MenuItem(_('Delete'))
            delete.connect('activate', self.__delete, info['uid'])
            menu.append(delete)
        return menu
        
    def __build_delete_dm_item(self, menu, info):
        delete = gtk.MenuItem(_('Delete'))
        delete.connect('activate', self.__delete_direct, info['uid'])
        menu.append(delete)
        return menu
    
    def __build_fav_item(self, menu, info):
        if info['fav']:
            unsave = gtk.MenuItem(_('- Fav'))
            unsave.connect('activate', self.__fav, False, info['uid'])
            menu.append(unsave)
        else:
            save = gtk.MenuItem(_('+ Fav'))
            save.connect('activate', self.__fav, True, info['uid'])
            menu.append(save)
        return menu
    
    def __build_open_item(self, menu, info):
        _open = gtk.MenuItem(_('Open'))
        
        open_menu = gtk.Menu()
        
        total_urls = util.detect_urls(info['msg'])
        total_users = util.detect_mentions(info['msg'])
        total_tags = util.detect_hashtags(info['msg'])
        total_groups = util.detect_groups(info['msg'])
        
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
            hashtag = self.mainwin.request_hashtags_url() + h[1:]
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
            if m == info['user'] or m in exist:
                continue
            exist.append(m)
            user_prof = '/'.join([self.mainwin.request_profiles_url(), m[1:]])
            mentmenu = gtk.MenuItem(m)
            mentmenu.connect('button-release-event', self.__open_url_with_event, user_prof)
            open_menu.append(mentmenu)
            
        _open.set_submenu(open_menu)
        if (len(total_urls) > 0) or (len(total_users) > 0) or \
           (len(total_tags) > 0) or (len(total_groups) > 0):
            menu.append(_open)
        return menu
    
    def __build_in_reply_to_item(self, menu, info):
        if info['in_reply_id']:
            in_reply = gtk.MenuItem(_('In reply to'))
            in_reply.connect('activate', self.__in_reply_to, info['user'], info['in_reply_id'])
            menu.append(in_reply)
        return menu
        
    def __build_profile_item(self, menu, info):
        user_profile = '/'.join([self.mainwin.request_profiles_url(), info['user']])
        usermenu = gtk.MenuItem('@' + info['user'])
        usermenu.connect('activate', self.__open_url, user_profile)
        menu.append(usermenu)
        return menu
        
    def __build_mute_item(self, menu, info):
        if info.has_key('friend') and info['friend'] and not info['own']: 
            mute = gtk.MenuItem(_('Mute'))
            mute.connect('activate', self.__mute, info['user'])
            menu.append(mute)
        return menu
        
    def __build_follow_item(self, menu, info):
        if not info['own']:
            if not info.has_key('friend'):
                follow = gtk.MenuItem(_('Loading friends...'))
                follow.set_sensitive(False)
            elif info['friend'] is False:
                follow = gtk.MenuItem(_('Follow'))
                follow.connect('activate', self.__follow, True, info['user'])
            elif info['friend'] is True:
                follow = gtk.MenuItem(_('Unfollow'))
                follow.connect('activate', self.__follow, False, info['user'])
            menu.append(follow)
        return menu
        
    # ===================================================================
    # Menus
    # ===================================================================
    def __build_std(self, menu, info):
        menu = self.__build_reply_item(menu, info)
        menu = self.__build_repeat_item(menu, info)
        menu = self.__build_direct_item(menu, info)
        menu = self.__build_delete_item(menu, info)
        menu = self.__build_fav_item(menu, info)
        menu = self.__build_open_item(menu, info)
        menu = self.__build_in_reply_to_item(menu, info)
        menu = self.__build_separator(menu)
        menu = self.__build_profile_item(menu, info)
        menu = self.__build_mute_item(menu, info)
        menu = self.__build_follow_item(menu, info)
        return menu
        
    def __build_dm(self, menu, info):
        menu = self.__build_reply_dm_item(menu, info)
        menu = self.__build_delete_dm_item(menu, info)
        menu = self.__build_open_item(menu, info)
        menu = self.__build_separator(menu)
        menu = self.__build_profile_item(menu, info)
        return menu
        
    def __build_profile(self, menu, info):
        return menu
        
    # ===================================================================
    # Unique public method
    # ===================================================================
    def build(self, uid, user, msg, in_reply_id, utype, protocol, own):
        info = self.__request_popup_info(uid, user)
        info['own'] = own
        info['uid'] = uid
        info['user'] = user
        info['msg'] = msg
        info['protocol'] = protocol
        info['in_reply_id'] = in_reply_id
        
        menu = gtk.Menu()
        if info.has_key('marking_fav'):
            menu = self.__build_busy_item(menu, _('Marking favorite...'))
            return menu
        elif info.has_key('unmarking_fav'):
            menu = self.__build_busy_item(menu, _('Unmarking favorite...'))
            return menu
        elif info.has_key('deleting'):
            menu = self.__build_busy_item(menu, _('Deleting...'))
            return menu
            
        if utype == UPDATE_TYPE_STD:
            menu = self.__build_std(menu, info)
        elif utype == UPDATE_TYPE_DM:
            menu = self.__build_dm(menu, info)
        elif utype == UPDATE_TYPE_PROFILE:
            menu = self.__build_profile(menu, info)
        return menu


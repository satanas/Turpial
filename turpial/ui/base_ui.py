# -*- coding: utf-8 -*-

"""Clase Base para todas las interfaces gráficas de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 07, 2009

import os
import locale
import gettext
import logging
import webbrowser
import subprocess

from turpial.ui import util

log = logging.getLogger('BaseUI')

class BaseGui:
    '''Parent class for every UI interface'''
    def __init__(self, controller):
        self.__controller = controller
        self.__user_pics = {}
        self.__queued_pics = []
        self.updating = [False, False, False]
        
        self.columns_lists = {}
        self.columns_viewed = []
        
        # Reescritos en la clase hija
        self.imgdir = ''
        
        # Initialize gettext
        gettext_domain = 'turpial'
        # Definicion de localedir en modo desarrollo
        if os.path.isdir(os.path.join(os.path.dirname(__file__), '..', 'i18n')):
            localedir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'i18n'))
            trans = gettext.install(gettext_domain, localedir)
            log.debug('LOCALEDIR: %s' % localedir)
        else:
            trans = gettext.install(gettext_domain)
            
    # ------------------------------------------------------------
    # Private/Internal methods
    # ------------------------------------------------------------
    
    def __done_user_avatar(self, user, pic):
        '''Execute when the user avatar is downloaded'''
        log.debug('Actualizando imagen de usuario %s' % user)
        self.resize_avatar(pic)
        self.__user_pics[user] = pic
        self.__queued_pics.remove(pic)
        self.update_user_avatar(user, pic)
    
    # ------------------------------------------------------------
    # Common methods to all interfaces
    # ------------------------------------------------------------
    
    def open_url(self, url):
        '''Open a URL in the configured web browser'''
        browser = self.__controller.config.read('Browser', 'cmd')
        if browser != '':
            log.debug('Abriendo URL %s con %s' % (url, browser))
            subprocess.Popen([browser, url])
        else:
            log.debug('Abriendo URL %s con navegador predeterminado' % url)
            webbrowser.open(url)
        
    def avatar_info_from_url(self, pic_url):
        '''Returns path and filename from the avatar URL'''
        pic = pic_url.replace('http://', '0_')
        pic = pic.replace('/', '_')
        return os.path.join(self.imgdir, pic), pic
        
    def current_avatar_path(self, pic_url):
        '''Returns the current path of an avatar'''
        pic = pic_url.replace('http://', '0_')
        pic = pic.replace('/', '_')
        path = os.path.join(self.imgdir, pic)
        default = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', 'data', 'pixmaps', 'unknown.png'))
        if os.path.isfile(path):
            return path
        else:
            return default
    
    def parse_tweet(self, xtweet):
        '''Decompose tweet in basic parts'''
        xtweet.text = util.unescape_text(xtweet.text)
        xtweet.source = util.detect_client(xtweet)
        return xtweet
        
    def after_destroy_status(self, timeline, favs):
        '''Update columns after destroy a status'''
        self.update_timeline(timeline)
        self.update_favorites(favs)
        
    def after_destroy_direct(self, directs):
        '''Update columns after destroy a direct'''
        self.update_directs(directs)
        
    def read_config_value(self, section, option):
        '''Read specific value from config'''
        return self.__controller.config.read(section, option)
        
    def read_config(self):
        '''Read all the user config'''
        return self.__controller.config.read_all()
        
    def read_global_config(self):
        '''Read all the global config'''
        return self.__controller.global_cfg.read_all()
        
    def save_config(self, new_config, update=True):
        '''Saves the user config'''
        self.__controller.save_config(new_config, update)
        
    def save_global_config(self, new_config):
        '''Saves the global config'''
        self.__controller.save_global_config(new_config)
    
    def request_remember(self, username, password, protocol, rem=False):
        '''Request remember'''
        self.__controller.remember(username, password, protocol, rem)
        
    def request_remembered(self, protocol):
        '''Request simple signin'''
        return self.__controller.get_remembered(protocol)
    
    def request_signin(self, username, password, protocol):
        '''Request simple signin'''
        self.__controller.signin(username, password, protocol)
        
    def request_signout(self):
        '''Request signout'''
        self.__controller.signout()
        
    def request_user_profile(self):
        '''Returns user profile'''
        return self.__controller.profile
        
    def request_user_avatar(self, user, pic_url):
        '''Download user avatar'''
        fullname, pic = self.avatar_info_from_url(pic_url)
        
        if os.path.isfile(fullname):
            self.__user_pics[user] = pic
            return self.__user_pics[user]
        if user in self.__user_pics: 
            return self.__user_pics[user]
        if pic in self.__queued_pics: 
            return None
        
        log.debug('Solicitando imagen de usuario %s' % user)
        self.__queued_pics.append(pic)
        self.__controller.download_user_pic(user, pic_url,
                                            self.__done_user_avatar)
        return None
        
    def request_repeat(self, id):
        '''Repeat status'''
        self.__controller.repeat(id)
        
    def request_fav(self, id):
        '''Mark a tweet as favorite'''
        self.__controller.set_favorite(id)
        
    def request_unfav(self, id):
        '''Unmark a tweet as favorite'''
        self.__controller.unset_favorite(id)
        
    def request_mute(self, user):
        '''Mute some user'''
        self.__controller.mute(user)
        
    def request_unmute(self, user):
        '''Unmute some user'''
        self.__controller.unmute(user)
        
    def request_follow(self, user):
        '''Follow some user'''
        self.__controller.follow(user)
        
    def request_unfollow(self, user):
        '''Unfollow some user'''
        self.__controller.unfollow(user)
        
    def request_direct(self, user, message):
        '''Send direct message'''
        log.debug('Enviando mensaje directo a %s' % user)
        
    def request_destroy_status(self, id):
        '''Destroy a tweet'''
        self.__controller.destroy_status(id)
        
    def request_short_url(self, longurl, callback):
        '''Short URL'''
        self.__controller.short_url(longurl, callback)
        
    def request_upload_pic(self, filename, message, callback):
        '''Upload a pic'''
        self.__controller.upload_pic(filename, message, callback)
        
    def request_update_status(self, text, in_reply_id):
        '''Tweet'''
        self.__controller.update_status(text, in_reply_id)
        
    def request_update_profile(self, name, url, bio, location):
        '''Update user profile'''
        self.__controller.update_profile(name, url, bio, location)
        
    def request_search(self, topic):
        '''Search a topic in search.twitter.com'''
        self.__controller.search(topic)
        
    def request_trends(self):
        '''Get trendings'''
        self.__controller._update_trends()
        
    def request_popup_info(self, tweet_id, user):
        '''Request info to show popup menu'''
        return self.__controller.get_popup_info(tweet_id, user)
        
    def request_conversation(self, tweet_id, user):
        '''Get tweets replied like a conversation'''
        self.__controller.get_conversation(tweet_id)
        
    def request_muted_list(self):
        '''Get the muted list'''
        return self.__controller.get_muted_list()
        
    def request_destroy_direct(self, id):
        '''Destroy a direct message'''
        self.__controller.destroy_direct(id)
        
    def request_friends_list(self):
        '''Get the friends list'''
        return self.__controller.get_friends()
        
    def request_hashtags_url(self):
        '''Get the hashtag url'''
        return self.__controller.get_hashtags_url()
        
    def request_groups_url(self):
        '''Get the groups url'''
        return self.__controller.get_groups_url()
        
    def request_profiles_url(self):
        '''Get the profiles url'''
        return self.__controller.get_profiles_url()
        
    def request_viewed_columns(self):
        '''Get the array for viewed columns'''
        return self.__controller.get_viewed_columns()
        
    def request_change_column(self, index, new_id):
        ''' Change the column at index for the indicated by new_id '''
        self.__controller.change_column(index, new_id)
        
    def request_is_friend(self, user):
        ''' Ask if a user is friend or not '''
        self.__controller.is_friend(user)
        
    def manual_update(self, id):
        if id == 0:
            self.download_column1()
        elif id == 1:
            self.download_column2()
        elif id == 2:
            self.download_column3()
    
    def update_timeline(self, tweets):
        if self.columns_viewed[0].id == 'timeline':
            self.update_column1(tweets)
        elif self.columns_viewed[1].id == 'timeline':
            self.update_column2(tweets)
        elif self.columns_viewed[2].id == 'timeline':
            self.update_column3(tweets)
            
    def update_directs(self, tweets):
        if self.columns_viewed[0].id == 'directs':
            self.update_column1(tweets)
        elif self.columns_viewed[1].id == 'directs':
            self.update_column2(tweets)
        elif self.columns_viewed[2].id == 'directs':
            self.update_column3(tweets)
        
    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------
    # Estos métodos deben ser llamados por la clase hija cada cierto tiempo
    
    def download_column1(self):
        if self.updating[0]: return True
        
        self.updating[0] = True
        self.__controller._update_column1()
        return True
        
    def download_column2(self):
        if self.updating[1]: return True
        
        self.updating[1] = True
        self.__controller._update_column2()
        return True
        
    def download_column3(self):
        if self.updating[2]: return True
        
        self.updating[2] = True
        self.__controller._update_column3()
        return True
        
    def download_rates(self):
        self.__controller._update_rate_limits()
        return True
        
    def download_favorites(self):
        self.__controller._update_favorites()
        return True
        
    def download_friends(self):
        self.__controller._update_friends()
        return True
        
    # ------------------------------------------------------------
    # Methods to be overwritten
    # ------------------------------------------------------------
    
    def resize_avatar(self, pic):
        raise NotImplementedError
        
    def main_loop(self):
        raise NotImplementedError
        
    def show_login(self):
        raise NotImplementedError
        
    def show_main(self, config, global_config, profile):
        raise NotImplementedError
        
    def set_lists(self, lists, viewed):
        raise NotImplementedError
        
    def show_oauth_pin_request(self, url):
        raise NotImplementedError
        
    def cancel_login(self):
        raise NotImplementedError
        
    def start_updating_column1(self):
        raise NotImplementedError
        
    def start_updating_column2(self):
        raise NotImplementedError
        
    def start_updating_column3(self):
        raise NotImplementedError
        
    def start_search(self):
        raise NotImplementedError
        
    def update_tweet(self, tweet):
        raise NotImplementedError
        
    def update_column1(self, tweets):
        raise NotImplementedError
        
    def update_column2(self, replies):
        raise NotImplementedError
        
    def update_column3(self, directs):
        raise NotImplementedError
        
    def update_favorites(self, favs):
        raise NotImplementedError
        
    def update_rate_limits(self, rates):
        raise NotImplementedError
        
    def update_follow(self, user, follow):
        raise NotImplementedError
        
    def update_user_avatar(self, user, avatar):
        raise NotImplementedError
        
    def update_user_profile(self, profile):
        raise NotImplementedError
        
    def update_search(self, topics):
        raise NotImplementedError
        
    def update_in_reply_to(self, tweets):
        raise NotImplementedError
        
    def update_conversation(self, tweets):
        raise NotImplementedError
        
    def tweet_changed(self, timeline, replies, favs):
        raise NotImplementedError
        
    def tweet_done(self, tweets):
        raise NotImplementedError
        
    def update_config(self, config):
        raise NotImplementedError
    
    def set_column_item(self, index, reset=False):
        raise NotImplementedError
            
    def quit(self, arg):
        raise NotImplementedError
        

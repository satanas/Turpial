#!/usr/bin/python
# -*- coding: utf-8 -*-

# Controlador de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 8, 2009

import os
import urllib
import logging

from ui import *
from api import *
from config import *
from optparse import OptionParser

try:
    import ctypes
    libc = ctypes.CDLL('libc.so.6')
    libc.prctl(15, 'turpial', 0, 0)
except:
    pass

class Turpial:
    def __init__(self):
        parser = OptionParser()
        parser.add_option('-d', '--debug', dest='debug', action='store_true',
            help='Debug Mode', default=False)
        parser.add_option('-i', '--interface', dest='interface',
            help='Select interface to use. (cmd|gtk)', default='gtk')
        parser.add_option('-c', '--clean', dest='clean', action='store_true',
            help='Clean all bytecodes', default=False)
        
        (options, _) = parser.parse_args()
        
        if options.debug: 
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('Controller')
        
        if options.clean:
            self.__clean()
            self.signout()
            
        self.interface = options.interface
        if options.interface == 'gtk':
            self.ui = gtk_ui_main.Main(self)
        else:
            self.ui = cmd_ui.Main(self)
        
        self.config = None
        self.profile = None
        self.httpserv = HTTPServices()
        self.picserv = HTTPServices()
        self.api = TurpialAPI()
        
        self.log.debug('Iniciando Turpial')
        self.httpserv.start()
        self.picserv.start()
        self.api.start()
        
        self.ui.show_login()
        self.ui.main_loop()
        
    def __clean(self):
        self.log.debug("Limpiando la casa...")
        i = 0
        for root, dirs, files in os.walk('.'):
            for f in files:
                path = os.path.join(root, f)
                if path.endswith('.pyc') or path.endswith('.pyo'): 
                    self.log.debug("Borrado %s" % path)
                    os.remove(path)

            
    def __validate_signin(self, val):
        if val.has_key('error'):
            self.ui.cancel_login(val['error'])
        else:
            self.profile = val
            self.ui.update_user_profile(val)
            self.ui.show_main(self.config, val)
            
            self._update_timeline()
            self._update_replies()
            #self._update_directs()
            self._update_favorites()
            self._update_rate_limits()
            
    def __validate_credentials(self, val):
        if val.has_key('error'):
            self.ui.cancel_login(val['error'])
        else:
            self.profile = val
            self.config = ConfigHandler(val['screen_name'])
            self.picserv.update_img_dir(self.config.imgdir)
            auth = self.config.read_section('Auth')
            self.api.start_oauth(auth, self.ui.show_oauth_pin_request, self.__signin_done)
    
    def __done_follow(self, friends, profile, user, follow):
        self.ui.update_user_profile(profile)
        self.ui.update_friends(friends)
        self.ui.update_follow(user, follow)
        #self.ui.update_timeline(friends)
        
    def __tweet_done(self, tweet):
        if tweet:
            self.profile['statuses_count'] += 1
            self.ui.update_user_profile(self.profile)
        self.ui.tweet_done(tweet)
        
    def __signin_done(self, key, secret, verifier):
        self.config.write('Auth', 'oauth-key', key)
        self.config.write('Auth', 'oauth-secret', secret)
        self.config.write('Auth', 'oauth-verifier', verifier)
        
        self.api.muted_users = self.config.load_muted_list()
        
        self.ui.show_main(self.config, self.profile)
        self._update_timeline()
        #self._update_replies()
        #self._update_directs()
        #self._update_rate_limits()
        #self._update_favorites()
        self._update_friends()
        
    def _update_timeline(self):
        self.ui.start_updating_timeline()
        tweets = int(self.config.read('General', 'num-tweets'))
        self.api.update_timeline(self.ui.update_timeline, tweets)
        
    def _update_replies(self):
        self.ui.start_updating_replies()
        tweets = int(self.config.read('General', 'num-tweets'))
        self.api.update_replies(self.ui.update_replies, tweets)
        
    def _update_directs(self):
        self.ui.start_updating_directs()
        tweets = int(self.config.read('General', 'num-tweets'))
        self.api.update_directs(self.ui.update_directs, tweets)
        
    def _update_favorites(self):
        self.api.update_favorites(self.ui.update_favorites)
    
    def _update_rate_limits(self):
        self.api.update_rate_limits(self.ui.update_rate_limits)
        
    def _update_friends(self):
        self.api.get_friends(self.ui.update_friends)
        
    def signin(self, username, password):
        self.config = ConfigHandler(username)
        self.api.auth(username, password, self.__validate_signin)
        
    def signin_oauth(self, username, password):
        self.api.auth(username, password, self.__validate_credentials)
        
    def auth_token(self, pin):
        self.api.authorize_oauth_token(pin, self.__signin_done)
        
    def signout(self):
        self.save_muted_list()
        self.log.debug('Desconectando')
        exit(0)
        #self.httpserv.quit()
        #if self.profile: 
        #    self.api.end_session()
        #else:
        #    self.api.quit()
    
    def update_status(self, text, reply_id=None):
        self.api.update_status(text, reply_id, self.__tweet_done)
        
    def destroy_status(self, tweet_id):
        self.api.destroy_status(tweet_id, self.ui.after_destroy)
        
    def set_favorite(self, tweet_id):
        self.api.set_favorite(tweet_id, self.ui.update_favorites)
        
    def unset_favorite(self, tweet_id):
        self.api.unset_favorite(tweet_id, self.ui.update_favorites)
    
    def retweet(self, tweet_id):
        self.api.retweet(tweet_id, self.ui.tweet_changed)
    
    def follow(self, user):
        self.api.follow(user, self.__done_follow)
        
    def unfollow(self, user):
        self.api.unfollow(user, self.__done_follow)
        
    def update_profile(self, new_name, new_url, new_bio, new_location):
        self.api.update_profile(new_name, new_url, new_bio, new_location, 
            self.ui.update_user_profile)
    
    def in_reply_to(self, twt_id):
        self.api.in_reply_to(twt_id, self.ui.update_in_reply_to)
        
    def get_conversation(self, twt_id):
        self.api.get_conversation(twt_id, self.ui.update_conversation)
        
    def mute(self, user):
        self.ui.start_updating_timeline()
        self.api.mute(user, self.ui.update_timeline)
        
    def short_url(self, text, callback):
        service = self.config.read('Services', 'shorten-url')
        self.httpserv.short_url(service, text, callback)
    
    def download_user_pic(self, user, pic_url, callback):
        self.picserv.download_pic(user, pic_url, callback)
        
    def upload_pic(self, path):
        pass
        
    def search_topic(self, query):
        self.ui.start_search()
        self.api.search_topic(query, self.ui.update_search_topics)
        
    def get_popup_info(self, tweet_id, user):
        if tweet_id in self.api.to_fav:
            return {'busy': 'Marcando favorito...'}
        elif tweet_id in self.api.to_unfav:
            return {'busy': 'Desmarcando favorito...'}
        elif tweet_id in self.api.to_del:
            return {'busy': 'Borrando...'}
            
        rtn = {}
        if self.api.friendsloaded:
            rtn['friend'] = self.api.is_friend(user)

        rtn['fav'] = self.api.is_fav(tweet_id)
        rtn['own'] = (self.profile['screen_name'] == user)
        
        return rtn
        
    def save_config(self, config, update):
        self.config.save(config)
        if update: self.ui.update_config(self.config)
        
    def save_muted_list(self):
        self.config.save_muted_list(self.api.muted_users)
        
    def get_muted_list(self):
        if self.api.friendsloaded:
            friends = []
            for f in self.api.friends:
                friends.append(f['screen_name'])
            
            return friends, self.api.muted_users
        else:
            return None, None
            
    def update_muted(self, muted_users):
        self.ui.start_updating_timeline()
        timeline = self.api.mute(muted_users, self.ui.update_timeline)
        
if __name__ == '__main__':
    t = Turpial()

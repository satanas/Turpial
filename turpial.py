#!/usr/bin/python
# -*- coding: utf-8 -*-

# Controlador de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 8, 2009

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
        
        (options, _) = parser.parse_args()
        
        if options.debug: 
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('Controller')
        
        self.interface = options.interface
        if options.interface == 'gtk':
            self.ui = gtk_ui_main.Main(self)
        else:
            self.ui = cmd_ui.Main(self)
        
        self.config = None
        self.profile = None
        self.agent = 'Turpial'
        self.httpserv = HTTPServices()
        self.picserv = HTTPServices()
        self.api = TurpialAPI()
        
        self.log.debug('Iniciando Turpial')
        self.httpserv.start()
        self.picserv.start()
        self.api.start()
        
        self.ui.show_login()
        self.ui.main_loop()
        
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
            auth = self.config.read_section('Auth')
            self.api.start_oauth(auth, self.ui.show_oauth_pin_request, self.__signin_done)
        
    def __tweet_done(self, tweet):
        if tweet:
            self.profile['statuses_count'] += 1
            self.ui.update_user_profile(self.profile)
        self.ui.tweet_done(tweet)
        
    def __signin_done(self, key, secret, verifier):
        self.config.write('Auth', 'oauth-key', key)
        self.config.write('Auth', 'oauth-secret', secret)
        self.config.write('Auth', 'oauth-verifier', verifier)
        
        self.ui.show_main(self.config, self.profile)
        self._update_timeline()
        self._update_replies()
        self._update_directs()
        self._update_favorites()
        self._update_rate_limits()
        
    def _update_timeline(self):
        self.ui.start_updating_timeline()
        self.api.update_timeline(self.ui.update_timeline, 60)
        
    def _update_replies(self):
        self.ui.start_updating_replies()
        self.api.update_replies(self.ui.update_replies)
        
    def _update_directs(self):
        self.ui.start_updating_directs()
        self.api.update_directs(self.ui.update_directs)
        
    def _update_favorites(self):
        self.api.update_favorites(self.ui.update_favorites)
    
    def _update_rate_limits(self):
        self.api.update_rate_limits(self.ui.update_rate_limits)
        
    def signin(self, username, password):
        self.config = ConfigHandler(username)
        self.api.auth(username, password, self.__validate_signin)
        
    def signin_oauth(self, username, password):
        self.api.auth(username, password, self.__validate_credentials)
        
    def auth_token(self, pin):
        self.api.authorize_oauth_token(pin, self.__signin_done)
        
    def signout(self):
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
        self.api.destroy_status(tweet_id, self.ui.update_timeline)
        
    def set_favorite(self, tweet_id):
        self.api.set_favorite(tweet_id, self.ui.tweet_changed)
        
    def unset_favorite(self, tweet_id):
        self.api.unset_favorite(tweet_id, self.ui.tweet_changed)
        
    
    def retweet(self, tweet_id):
        self.api.retweet(tweet_id, self.ui.tweet_changed)
    
    '''
    def mute(self, user):
        if user not in self.muted_users: 
            self.muted_users.append(user)
            self.log.debug('Muteando a %s' % user)
            self.ui.update_timeline(self.__get_timeline())
            
    def unmute(self, user):
        if user in self.muted_users: 
            self.muted_users.remove(user)
            self.log.debug('Desmuteando a %s' % user)
            self.ui.update_timeline(self.__get_timeline())
    '''
    def short_url(self, text, callback):
        service = 'is.gd'
        self.httpserv.short_url(service, text, callback)
    
    def download_user_pic(self, user, pic_url, callback):
        self.picserv.download_pic(user, pic_url, callback)
        
    def upload_pic(self, path):
        pass
        
    def search_topic(self, query):
        self.api.search_topic(query, self.ui.update_search_topics)
        
    def save_config(self, config):
        self.log.debug('Guardando configuracion')
        print config
        self.config.save(config)
        self.ui.update_config(self.config)
        
if __name__ == '__main__':
    t = Turpial()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Controlador de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 8, 2009

import urllib
import logging
import threading

from api import *
from ui import *
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
            help='Select interface to use. (cmd|gtk)', default='cmd')
        
        (options, _) = parser.parse_args()
        
        if options.debug: 
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('Controller')
        
        self.interface = options.interface
        if options.interface == 'gtk':
            self.ui = gtk_ui.Main(self)
        else:
            self.ui = cmd_ui.Main(self)
            
        self.twitter = None
        self.search = Twitter(domain="search.twitter.com")
        self.agent = 'Turpial'
        self.timer_tl = None
        self.timer_rp = None
        self.timer_dm = None
        
        # Esto deberia ir en el modelo
        self.profile = None
        self.tweets = []
        self.replies = []
        self.directs = []
        self.directs_sent = []
        self.favs = []
        self.rate_limits = []
        self.muted_users = []
        # ==============================
        
        self.log.debug('Iniciando Turpial')
        self.ui.show_login()
        self.ui.main_loop()
    
    # Lo que sigue a continuación también debería ir en el modelo
    # ==============================================================
    def get_timeline(self):
        if len(self.muted_users) == 0: return self.tweets
        tweets = []
        for twt in self.tweets:
            if twt['user']['screen_name'] not in self.muted_users:
               tweets.append(twt)
        return tweets
    # ==============================================================
    
    def __update_timeline(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Timeline')
        self.tweets = self.twitter.statuses.friends_timeline()
        if rate: self.update_rate_limits()
        self.ui.update_timeline(self.get_timeline())
        
        self.timer_tl = threading.Timer(200, self.__update_timeline)
        self.timer_tl.start()
    
    def __update_replies(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Replies')
        self.replies = self.twitter.statuses.mentions()
        if rate: self.update_rate_limits()
        self.ui.update_replies(self.replies)
        
        self.timer_rp = threading.Timer(600, self.__update_replies)
        self.timer_rp.start()
        
    def __update_directs(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Directs')
        self.directs = self.twitter.direct_messages()
        self.directs_sent = self.twitter.direct_messages.sent()
        if rate: self.update_rate_limits()
        self.ui.update_directs(self.directs, self.directs_sent)
        
        self.timer_dm = threading.Timer(900, self.__update_directs)
        self.timer_dm.start()
        
    def __update_favs(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Favorites')
        self.favs = self.twitter.favorites()
        if rate: self.update_rate_limits()
        self.ui.update_favs(self.favs)
        
    def signin(self, username, password):
        self.twitter = Twitter(email=username, password=password, agent=self.agent)
        try:
            self.profile = self.twitter.account.verify_credentials()
            
            self.__update_timeline(False)
            self.__update_replies(False)
            self.__update_favs(False)
            self.__update_directs()
            
            self.ui.show_main()
            self.ui.update_rate_limits(self.rate_limits)
            
        except TwitterError, error:
            self.log.debug('Error verificando credenciales %s' % error)
            self.ui.cancel_login(u'Información de usuario inválida')
            
    def signout(self):
        self.log.debug('Desconectando')
        if self.twitter: self.twitter.account.end_session()
        self.log.debug('Terminando hilos')
        if self.timer_tl: self.timer_tl.cancel()
        if self.timer_rp: self.timer_rp.cancel()
        if self.timer_dm: self.timer_dm.cancel()
        
    def get_trends(self):
        return self.search.trends()
        
    def get_rate_limits(self):
        self.__update_rate_limits()
        return self.rate_limits
        
    def get_following(self):
        return self.twitter.statuses.friends()
        
    def get_followers(self):
        return self.twitter.statuses.followers()
        
    def search_people(self, query):
        query = urllib.quote(query)
        return self.twitter.users.search(q=query)
    
    def update_status(self, text):
        rtn = self.twitter.statuses.update(status=text)
        self.tweets.insert(0, rtn)
        
    def destroy_status(self, tweet_id):
        item = None
        rtn = self.twitter.statuses.destroy(id=tweet_id)
        for twt in self.tweets:
            if tweet_id == twt['id']:
                item = twt
                break
        if item: self.tweets.remove(item)
        
    def update_rate_limits(self):
        self.rate_limits = self.twitter.account.rate_limit_status()
        return self.rate_limits
        
    def set_favorite(self, tweet_id):
        rtn = self.twitter.favorites.create(id=tweet_id)
        self.favs.insert(0, rtn)
    
    def unset_favorite(self, tweet_id):
        item = None
        rtn = self.twitter.favorites.destroy(id=tweet_id)
        for fav in self.favs:
            if tweet_id == fav['id']:
                item = fav
                break
        if item: self.favs.remove(item)
        
    def send_direct(self, user, msg):
        self.twitter.direct_messages.new(screen_name=user, text=msg)
        
    def update_profile(self, new_name=None, new_url=None, new_bio=None, new_location=None):
        if new_name is not None:
            self.twitter.account.update_profile(name=new_name)
        if new_url is not None:
            self.twitter.account.update_profile(url=new_url)
        if new_bio is not None:
            self.twitter.account.update_profile(description=new_bio)
        if new_location is not None:
            self.twitter.account.update_profile(location=new_location)
    
    def mute(self, user):
        if user not in self.muted_users: 
            self.muted_users.append(user)
            self.log.debug('Muteando a %s' % user)
            
    def unmute(self, user):
        if user in self.muted_users: 
            self.muted_users.remove(user)
            self.log.debug('Desmuteando a %s' % user)
        
    def follow(self, user):
        self.twitter.friendships.create(screen_name=user)
        self.log.debug('Follow to %s' % user)
        
    def unfollow(self, user):
        self.twitter.friendships.destroy(screen_name=user)
        self.log.debug('Unfollow to %s' % user)
        
if __name__ == '__main__':
    t = Turpial()

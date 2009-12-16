#!/usr/bin/python
# -*- coding: utf-8 -*-

# Controlador de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 8, 2009

import urllib
import logging
import threading

from ui import *
from api import *
from services import *
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
        #self.timer_tl = None
        #self.timer_rp = None
        #self.timer_dm = None
        self.httpserv = HTTPServices()
        
        # Esto deberia ir en el modelo
        self.profile = None
        self.tweets = []
        self.replies = []
        self.directs = []
        self.directs_sent = []
        self.favs = []
        self.followers = []
        self.following = []
        self.rate_limits = []
        self.muted_users = []
        # ==============================
        
        self.log.debug('Iniciando Turpial')
        self.ui.show_login()
        self.ui.main_loop()
        
    def __update_timeline(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Timeline')
        self.tweets = self.twitter.statuses.friends_timeline()
        if rate: self.update_rate_limits()
        self.ui.update_timeline(self.get_timeline())
        
    def __update_replies(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Replies')
        self.replies = self.twitter.statuses.mentions()
        if rate: self.update_rate_limits()
        self.ui.update_replies(self.replies)
        
    def __update_directs(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Directs')
        self.directs = self.twitter.direct_messages()
        self.directs_sent = self.twitter.direct_messages.sent()
        if rate: self.update_rate_limits()
        self.ui.update_directs(self.directs, self.directs_sent)
        
    def __update_favs(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Favorites')
        self.favs = self.twitter.favorites()
        if rate: self.update_rate_limits()
        self.ui.update_favs(self.favs)
        
    def __update_following(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Actualizando Following')
        self.following = self.twitter.statuses.friends()
        if rate: self.update_rate_limits()
        self.ui.update_following(self.following)
        
    def __update_followers(self):
        if self.interface != 'cmd': self.log.debug('Actualizando Followers')
        self.followers = self.twitter.statuses.followers()
        if rate: self.update_rate_limits()
        self.ui.update_followers(self.followers)
        
        return self.twitter.statuses.followers()
        
    def start_services(self):
        self.httpserv.start()
        
    def signin(self, username, password):
        
        self.twitter = Twitter(email=username, password=password, agent=self.agent)
        try:
            self.profile = self.twitter.account.verify_credentials()
            
            self.ui.show_main()
            
            self.__update_timeline(False)
            #self.__update_replies(False)
            #self.__update_directs()
            #self.__update_favs()
            self.__update_following()
            #self.__update_followers()
            
            self.ui.update_user_profile(self.profile)
            self.ui.update_rate_limits(self.rate_limits)
            
            self.start_services()
            
        except TwitterError, error:
            self.log.debug('Error verificando credenciales %s' % error)
            self.ui.cancel_login(u'Información de usuario inválida')
        
        #self.ui.show_main()
        
    def signout(self):
        self.httpserv.quit()
        self.log.debug('Desconectando')
        if self.twitter: self.twitter.account.end_session()
        
    def get_timeline(self):
        if len(self.muted_users) == 0: return self.tweets
        tweets = []
        for twt in self.tweets:
            if twt['user']['screen_name'] not in self.muted_users:
               tweets.append(twt)
        return tweets
        
    def get_trends(self):
        return self.search.trends()
        
    def search_people(self, query):
        query = urllib.quote(query)
        return self.twitter.users.search(q=query)
    
    def update_status(self, text, reply_to=None):
        if reply_to:
            rtn = self.twitter.statuses.update(status=text)
        else:
            rtn = self.twitter.statuses.update(status=text, in_reply_to_status_id=reply_to)
        self.log.debug(u'Nuevo tweet %s' % text)
        self.tweets.insert(0, rtn)
        self.ui.update_timeline(self.get_timeline())
        
    def destroy_status(self, tweet_id):
        item = None
        rtn = self.twitter.statuses.destroy(id=tweet_id)
        for twt in self.tweets:
            if tweet_id == twt['id']:
                item = twt
                break
        if item: self.tweets.remove(item)
        self.log.debug('Destruido tweet %s' % tweet_id)
        self.ui.update_timeline(self.get_timeline())
        
    def update_rate_limits(self):
        self.rate_limits = self.twitter.account.rate_limit_status()
        return self.rate_limits
        
    def update_following(self):
        #self.following = self.twitter.statuses.friends()
        self.ui.update_following(self.following)
        
    def update_followers(self):
        #self.followers = self.twitter.statuses.followers()
        self.ui.update_followers(self.followers)
        
    def set_favorite(self, tweet_id):
        rtn = self.twitter.favorites.create(id=tweet_id)
        self.log.debug('Marcado como favorito el tweet %s' % tweet_id)
        self.favs.insert(0, rtn)
        self.ui.update_favs(self.favs)
    
    def unset_favorite(self, tweet_id):
        item = None
        rtn = self.twitter.favorites.destroy(id=tweet_id)
        for fav in self.favs:
            if tweet_id == fav['id']:
                item = fav
                break
        if item: self.favs.remove(item)
        self.log.debug('Desmarcado como favorito el tweet %s' % tweet_id)
        self.ui.update_favs(self.favs)
        
    def send_direct(self, user, msg):
        self.twitter.direct_messages.new(screen_name=user, text=msg)
        self.log.debug('Enviado mensaje directo a %s' % user)
        
    def update_profile(self, new_name=None, new_url=None, new_bio=None, new_location=None):
        if new_name is not None and new_name != self.profile['name']:
            self.twitter.account.update_profile(name=new_name)
        if new_url is not None and new_url != self.profile['url']:
            self.twitter.account.update_profile(url=new_url)
        if new_bio is not None and new_bio != self.profile['description']:
            self.twitter.account.update_profile(description=new_bio)
        if new_location is not None and new_location != self.profile['location']:
            self.twitter.account.update_profile(location=new_location)
        self.ui.update_user_profile(self.profile)
    
    def mute(self, user):
        if user not in self.muted_users: 
            self.muted_users.append(user)
            self.log.debug('Muteando a %s' % user)
            self.ui.update_timeline(self.get_timeline())
            
    def unmute(self, user):
        if user in self.muted_users: 
            self.muted_users.remove(user)
            self.log.debug('Desmuteando a %s' % user)
            self.ui.update_timeline(self.get_timeline())
        
    def follow(self, user):
        rtn = self.twitter.friendships.create(screen_name=user)
        self.log.debug('Follow to %s' % user)
        self.following.insert(0, rtn)
        self.ui.update_following(self.following)
        
    def unfollow(self, user):
        item = None
        rtn = self.twitter.friendships.destroy(screen_name=user)
        for f in self.following:
            if user == f['screen_name']:
                item = f
                break
        if item: self.following.remove(item)
        self.log.debug('Unfollow to %s' % user)
        self.ui.update_following(self.following)
        
    def short_url(self, text, callback):
        service = 'tr.im'
        self.httpserv.short_url(service, text, callback)
    
    def download_user_pic(self, user, pic_url, callback):
        self.httpserv.download_pic(user, pic_url, callback)
        
if __name__ == '__main__':
    t = Turpial()

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
            self.ui = gtk_ui_main.Main(self)
        else:
            self.ui = cmd_ui.Main(self)
            
        self.twitter = None
        self.twitterapi = None
        self.search = Twitter(domain="search.twitter.com")
        self.agent = 'Turpial'
        self.httpserv = HTTPServices()
        self.api = TurpialAPI()
        
        self.muted_users = []
        
        self.log.debug('Iniciando Turpial')
        self.httpserv.start()
        self.api.start()
        
        self.ui.show_login()
        self.ui.main_loop()
        
    def __validate_signin(self, val):
        if val.has_key('error'):
            self.ui.cancel_login(val['error'])
        else:
            self.profile = val
            self.ui.update_user_profile(val)
            self.ui.show_main()
            
            self._update_timeline()
            self._update_replies()
            self._update_directs()
            #self._update_favorites()
            self._update_rate_limits()
        
    def _update_timeline(self):
        self.api.update_timeline(self.ui.update_timeline)
        
    def _update_replies(self):
        self.api.update_replies(self.ui.update_replies)
        
    def _update_directs(self):
        self.api.update_directs(self.ui.update_directs)
        
    def _update_favorites(self):
        self.api.update_favorites(self.ui.update_favs)
    '''
    def _update_following(self, rate=True):
        if self.interface != 'cmd': self.log.debug('Descargando Following')
        self.following = self.twitter.statuses.friends()
        self.ui.update_following(self.following)
        
    def _update_followers(self):
        if self.interface != 'cmd': self.log.debug('Descargando Followers')
        self.followers = self.twitter.statuses.followers()
        self.ui.update_followers(self.followers)
        
    def _update_trends(self):
        current = self.search.trends.current()
        day = self.search.trends.daily()
        week = self.search.trends.weekly()
        self.ui.update_trends(current, day, week)
    '''
    
    def _update_rate_limits(self):
        self.api.update_rate_limits(self.ui.update_rate_limits)
        
    def signin(self, username, password):
        self.api.auth(username, password, self.__validate_signin)
        
    def signout(self):
        self.log.debug('Desconectando')
        self.httpserv.quit()
        self.api.end_session()
        
    '''
    def search_people(self, query):
        query = urllib.quote(query)
        self.log.debug(u'Buscando personas con %s' % query)
        people = self.twitter.users.search(q=query)
        self.ui.update_search_people(people)
        
    def search_topic(self, topic):
        topic = urllib.quote(topic)[:140]
        self.log.debug(u'Buscando tweets sobre: %s' % topic)
        tweets = self.search.search(q=topic)
        self.ui.update_search_topics(tweets)
    '''
    def update_status(self, text, reply_id=None):
        self.api.update_status(text, reply_id, self.ui.update_timeline)
        
    def destroy_status(self, tweet_id):
        self.api.destroy_status(tweet_id, self.ui.update_timeline)
    '''
    def retweet(self, tweet_id):
        self.twitterapi.statuses.retweet(id=tweet_id)
        self.log.debug('Retuiteado tweet %s' % tweet_id)
        
    def set_favorite(self, tweet_id):
        rtn = self.twitter.favorites.create(id=tweet_id)
        self.favs.insert(0, rtn)
        index = None
        for twt in self.tweets:
            if tweet_id == str(twt['id']):
                index = self.tweets.index(twt)
                break
        if index is not None: self.tweets[index]['favorited'] = True
        
        self.log.debug('Marcado como favorito el tweet %s' % tweet_id)
        self.ui.update_favs(self.favs)
        self.ui.update_timeline(self.__get_timeline())
    
    def unset_favorite(self, tweet_id):
        rtn = self.twitter.favorites.destroy(id=tweet_id)
        item = None
        for fav in self.favs:
            if tweet_id == str(fav['id']):
                item = fav
                break
        if item: self.favs.remove(item)
        
        index = None
        for twt in self.tweets:
            if tweet_id == str(twt['id']):
                index = self.tweets.index(twt)
                break
        if index is not None: self.tweets[index]['favorited'] = False
        
        self.log.debug('Desmarcado como favorito el tweet %s' % tweet_id)
        self.ui.update_favs(self.favs)
        self.ui.update_timeline(self.__get_timeline())
        
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
            self.ui.update_timeline(self.__get_timeline())
            
    def unmute(self, user):
        if user in self.muted_users: 
            self.muted_users.remove(user)
            self.log.debug('Desmuteando a %s' % user)
            self.ui.update_timeline(self.__get_timeline())
        
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
    '''
    def short_url(self, text, callback):
        service = 'tr.im'
        self.httpserv.short_url(service, text, callback)
    
    def download_user_pic(self, user, pic_url, callback):
        self.httpserv.download_pic(user, pic_url, callback)
        
    def upload_pic(self, path):
        pass
        
if __name__ == '__main__':
    t = Turpial()

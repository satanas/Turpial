#!/usr/bin/python

# Controlador de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 8, 2009

#import time
import urllib
import logging
from api import *
from ui import *

logging.basicConfig(level=logging.DEBUG)

class Turpial:
    def __init__(self):
        self.twitter = None
        self.search = Twitter(domain="search.twitter.com")
        self.ui = cmdline.Main(self)
        self.agent = 'Turpial'
        
        self.tweets = []
        self.replies = []
        self.directs = []
        self.directs_sent = []
        self.favs = []
        self.rate_limits = []
        
        self.log = logging.getLogger('Controller')
        self.log.debug('Iniciando Turpial')
        self.ui.show_login()
        self.ui.main_loop()
        
    def __update_timeline(self, rate=True):
        self.tweets = self.twitter.statuses.friends_timeline()
        if rate: self.update_rate_limits()
    
    def __update_replies(self, rate=True):
        self.replies = self.twitter.statuses.mentions()
        if rate: self.update_rate_limits()
        
    def __update_directs(self, rate=True):
        self.directs = self.twitter.direct_messages()
        self.directs_sent = self.twitter.direct_messages.sent()
        if rate: self.update_rate_limits()
        
    def __update_favs(self, rate=True):
        self.favs = self.twitter.favorites()
        if rate: self.update_rate_limits()
        
    def signin(self, username, password):
        #self.ui.show_main()
        #self.ui.cancel_login('Login info not valid')
        #return
        self.twitter = Twitter(email=username, password=password, agent=self.agent)
        try:
            self.twitter.account.verify_credentials()
            #self.__update_timeline(False)
            #self.__update_replies(False)
            self.__update_directs()
            
            self.ui.show_main()
            self.ui.update_timeline(self.tweets)
            #self.ui.update_replies(self.replies)
            #self.ui.update_directs(self.direct, self.direct_sent)
            #self.ui.update_favorites(self.favs)
            self.ui.update_rate_limits(self.rate_limits)
        except TwitterError, error:
            self.log.debug('Error verificando credenciales %s' % error)
            self.ui.cancel_login('Login info not valid')
            
    def signout(self):
        self.twitter.account.end_session()
        
    def get_trends(self):
        return self.search.trends()
        
    def get_rate_limits(self):
        self.__update_rate_limits()
        return self.rate_limits
        
    def search_people(self, query):
        query = urllib.quote(query)
        return self.twitter.users.search(q=query)
    
    def update_status(self, text):
        rtn = self.twitter.statuses.update(status=text)
        self.tweets.insert(0, rtn)
        #return self.tweets[0]
        
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
        
if __name__ == '__main__':
    t = Turpial()

# -*- coding: utf-8 -*-

# Modelo base basado en hilos para el Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 22, 2009

import Queue
import urllib2
import logging
import threading

from base64 import b64encode
from urllib import urlencode

from twitter_globals import POST_ACTIONS

def _py26OrGreater():
    import sys
    return sys.hexversion > 0x20600f0

if _py26OrGreater():
    import json
else:
    import simplejson as json
    
class TurpialAPI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.log = logging.getLogger('API')
        self.queue = Queue.Queue()
        self.exit = False
        
        self.agent = 'Turpial'
        self.format = 'json'
        self.username = None
        self.password = None
        self.tweets = []
        self.muted_users = []
        self.favorites = []
        
        self.log.debug('Iniciado')
    
    def __register(self, args, callback):
        self.queue.put((args, callback))
        
    def __handle_tweets(self, tweet, args):
        if args.has_key('add'):
            self.tweets.insert(0, tweet)
        elif args.has_key('del'):
            item = None
            for twt in self.tweets:
                if tweet['id'] == twt['id']:
                    item = twt
                    break
            if item: self.tweets.remove(item)
            
        if len(self.muted_users) == 0: return self.tweets
        
        tweets = []
        for twt in self.tweets:
            if twt['user']['screen_name'] not in self.muted_users:
               tweets.append(twt)
        return tweets
        
    def auth(self, username, password, callback):
        self.username = username
        self.password = password
        self.__register({'uri': 'http://twitter.com/account/verify_credentials', 'login':True}, callback)
        
    def update_rate_limits(self, callback):
        self.__register({'uri': 'http://twitter.com/account/rate_limit_status'}, callback)
        
    def update_timeline(self, callback):
        self.log.debug('Descargando Timeline')
        self.__register({'uri': 'http://api.twitter.com/1/statuses/home_timeline', 'timeline': True}, callback)
        
    def update_replies(self, callback):
        self.log.debug('Descargando Replies')
        self.__register({'uri': 'http://twitter.com/statuses/mentions'}, callback)
        
    def update_directs(self, callback):
        self.log.debug('Descargando Directs')
        self.__register({'uri': 'http://twitter.com/direct_messages'}, callback)
        
    def update_favorites(self, callback):
        self.log.debug('Descargando Favorites')
        self.__register({'uri': 'http://twitter.com/favorites'}, callback)
        
    def update_status(self, text, in_reply_id, callback):
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}
        self.log.debug(u'Nuevo tweet: %s' % text)
        self.__register({'uri': 'http://twitter.com/statuses/update', 'args': args, 'tweet':True, 'add': True}, callback)
        
    def destroy_status(self, tweet_id, callback):
        args = {'id': tweet_id}
        self.log.debug('Destruyendo tweet: %s' % tweet_id)
        self.__register({'uri': 'http://twitter.com/statuses/destroy', 'args': args, 'tweet':True, 'del': True}, callback)
        
    def retweet(self, tweet_id, callback):
        args = {'id': tweet_id}
        self.__register({'uri': 'http://twitter.com/statuses/retweet', 'args': args}, callback)
        
    def end_session(self):
        self.__register({'uri': 'http://twitter.com/account/end_session', 'exit': True}, None)
        
    def quit(self):
        self.exit = True
        
    def run(self):
        while not self.exit:
            try:
                req = self.queue.get(False)
            except Queue.Empty:
                continue
            
            (args, callback) = req
            
            rtn = None
            method = "GET"
            uri = args['uri']
            
            for action in POST_ACTIONS:
                if uri.endswith(action): method = "POST"
            
            uri = "%s.%s" % (uri, self.format)
            
            argStr = ""
            argData = None
            encoded_args = None
            if args.has_key('args'):
                encoded_args = urlencode(args['args'])
            
            if (method == "GET"):
                if encoded_args: argStr = "?%s" %(encoded_args)
            else:
                argData = encoded_args

            headers = {}
            if (self.username):
                headers["Authorization"] = "Basic " + b64encode("%s:%s" %(self.username, self.password))
            
            req = urllib2.Request("%s%s" %(uri, argStr), argData, headers)
            try:
                handle = urllib2.urlopen(req)
                rtn = json.loads(handle.read())
            except urllib2.HTTPError, e:
                if (e.code == 304):
                    rtn = []
                else:
                    self.log.debug("Twitter sent status %i for URL: %s using parameters: (%s)\ndetails: %s" % (
                        e.code, uri, encoded_args, e.fp.read()))
                    if args.has_key('login'): 
                        rtn = {'error': 'Error %i from Twitter.com' % e.code}
            except urllib2.URLError, e:
                self.log.debug("Problem to connect to twitter.com. Check network status.\nDetails: %s" %(e))
                if args.has_key('login'): 
                    rtn = {'error': 'Can\'t connect to twitter.com'}
            
            if args.has_key('timeline'):
                self.tweets = rtn
                
            if args.has_key('tweet'):
                rtn = self.__handle_tweets(rtn, args)
            
            if args.has_key('exit'):
                self.exit = True
            else:
                callback(rtn)
            
        self.log.debug('Terminado')
        return

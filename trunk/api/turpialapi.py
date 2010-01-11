# -*- coding: utf-8 -*-

# Modelo base basado en hilos para el Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 22, 2009

import time
import oauth
import Queue
#import socket
import urllib2
import logging
import threading
import traceback

from base64 import b64encode
from urllib import urlencode

from oauth_client import TurpialAuthClient

from twitter_globals import *

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
        
        #socket.setdefaulttimeout(8)
        self.setDaemon(False)
        self.log = logging.getLogger('API')
        self.queue = Queue.Queue()
        self.exit = False
        
        # OAuth stuffs
        self.client = None
        self.consumer = None
        self.is_oauth = False
        self.token = None
        self.signature_method_hmac_sha1 = None
        
        self.format = 'json'
        self.username = None
        self.password = None
        self.tweets = []
        self.replies = []
        self.favorites = []
        self.muted_users = []
        
        self.log.debug('Iniciado')
    
    def __register(self, args, callback):
        self.queue.put((args, callback))
        
    def __handle_oauth(self, args, callback):
        if args['cmd'] == 'start':
            self.client = TurpialAuthClient()
            self.consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
            self.signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
            auth = args['auth']
            
            if auth['oauth-key'] != '' and auth['oauth-secret'] != '' and auth['oauth-verifier'] != '':
                self.token = oauth.OAuthToken(auth['oauth-key'], auth['oauth-secret'])
                self.token.set_verifier(auth['oauth-verifier'])
                self.is_oauth = True
                args['done'](self.token.key, self.token.secret, self.token.verifier)
            else:
                self.log.debug('Obtain a request token')
                oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_url=self.client.request_token_url)
                oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, None)
                
                self.log.debug('REQUEST (via headers)')
                self.log.debug('parameters: %s' % str(oauth_request.parameters))
                self.token = self.client.fetch_request_token(oauth_request)
                
                self.log.debug('GOT')
                self.log.debug('key: %s' % str(self.token.key))
                self.log.debug('secret: %s' % str(self.token.secret))
                self.log.debug('callback confirmed? %s' % str(self.token.callback_confirmed))
                
                self.log.debug('Authorize the request token')
                oauth_request = oauth.OAuthRequest.from_token_and_callback(token=self.token, http_url=self.client.authorization_url)
                self.log.debug('REQUEST (via url query string)')
                self.log.debug('parameters: %s' % str(oauth_request.parameters))
                callback(oauth_request.to_url())
        elif args['cmd'] == 'authorize':
            pin = args['pin']
            self.log.debug('Obtain an access token')
            oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.token, verifier=pin, http_url=self.client.access_token_url)
            oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, self.token)
            self.log.debug('REQUEST (via headers)')
            self.log.debug('parameters: %s' % str(oauth_request.parameters))
            self.token = self.client.fetch_access_token(oauth_request)
            self.log.debug('GOT')
            self.log.debug('key: %s' % str(self.token.key))
            self.log.debug('secret: %s' % str(self.token.secret))
            self.is_oauth = True
            callback(self.token.key, self.token.secret, pin)
            
    def __handle_tweets(self, tweet, args):
        if tweet is None: return False
        
        if args.has_key('add'):
            exist = False
            for twt in self.tweets:
                if tweet['id'] == twt['id']: exist = True
            
            if not exist: self.tweets.insert(0, tweet)
        elif args.has_key('del'):
            item = None
            for twt in self.tweets:
                if tweet['id'] == twt['id']:
                    item = twt
                    break
            if item: self.tweets.remove(item)
        return True
        
    def __handle_retweets(self, tweet):
        if tweet is None: return False
        
        index = None
        for twt in self.tweets:
            if tweet['id'] == twt['id']:
                index = self.tweets.index(twt)
                break
        if index: self.tweets[index]['retweeted_status'] = tweet['retweeted_status']
        
        index = None
        for twt in self.replies:
            if tweet['id'] == twt['id']:
                index = self.replies.index(twt)
                break
        if index: self.replies[index]['retweeted_status'] = tweet['retweeted_status']
        
        index = None
        for twt in self.favorites:
            if tweet['id'] == twt['id']:
                index = self.favorites.index(twt)
                break
        if index: self.favorites[index]['retweeted_status'] = tweet['retweeted_status']
        return True
        
    def __handle_muted(self):
        if len(self.muted_users) == 0: return self.tweets
        
        tweets = []
        for twt in self.tweets:
            if twt['user']['screen_name'] not in self.muted_users:
               tweets.append(twt)
               
        return tweets
        
    def __handle_favorites(self, tweet, fav):
        if tweet is None: return False
        
        if fav:
            tweet['favorited'] = True
            self.favorites.insert(0, tweet)
        else:
            item = None
            for f in self.favorites:
                if tweet['id'] == f['id']:
                    item = f
                    break
            if item: self.favorites.remove(item)
        
        index = None
        for twt in self.tweets:
            if tweet['id'] == twt['id']:
                index = self.tweets.index(twt)
                break
        if index: 
            self.tweets[index]['favorited'] = fav
        
        index = None
        for twt in self.replies:
            if tweet['id'] == twt['id']:
                index = self.replies.index(twt)
                break
        if index: 
            self.replies[index]['favorited'] = fav
        
        return True
        
    def auth(self, username, password, callback):
        self.log.debug('Iniciando autenticacion basica')
        self.username = username
        self.password = password
        self.__register({'uri': 'http://twitter.com/account/verify_credentials', 'login':True}, callback)
        
    def start_oauth(self, auth, show_pin_callback, done_callback):
        self.log.debug('Iniciando OAuth')
        self.__register({'cmd': 'start', 'oauth':True, 'auth': auth, 'done':done_callback}, show_pin_callback)
        
    def authorize_oauth_token(self, pin, callback):
        self.log.debug('Solicitando autenticacion del token')
        self.__register({'cmd': 'authorize', 'oauth':True, 'pin': pin}, callback)
        
    def update_rate_limits(self, callback):
        self.__register({'uri': 'http://twitter.com/account/rate_limit_status'}, callback)
        
    def update_timeline(self, callback, count=20):
        self.log.debug('Descargando Timeline')
        args = {'count': count}
        self.__register({'uri': 'http://api.twitter.com/1/statuses/home_timeline', 'args': args, 'timeline': True}, callback)
        
    def update_replies(self, callback):
        self.log.debug('Descargando Replies')
        self.__register({'uri': 'http://twitter.com/statuses/mentions', 'replies': True}, callback)
        
    def update_directs(self, callback):
        self.log.debug('Descargando Directs')
        self.__register({'uri': 'http://twitter.com/direct_messages'}, callback)
        
    def update_favorites(self, callback):
        self.log.debug('Descargando Favorites')
        self.__register({'uri': 'http://twitter.com/favorites', 'favorites': True}, callback)
        
    def update_status(self, text, in_reply_id, callback):
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}
        self.log.debug(u'Nuevo tweet: %s' % text)
        self.__register({'uri': 'http://twitter.com/statuses/update', 'args': args, 'tweet':True, 'add': True}, callback)
        
    def destroy_status(self, tweet_id, callback):
        #args = {'id': tweet_id}
        self.log.debug('Destruyendo tweet: %s' % tweet_id)
        self.__register({'uri': 'http://twitter.com/statuses/destroy', 'id': tweet_id, 'args': '', 'tweet':True, 'del': True}, callback)
        
    def retweet(self, tweet_id, callback):
        self.log.debug('Retweet: %s' % tweet_id)
        self.__register({'uri': 'http://api.twitter.com/1/statuses/retweet',  'id':tweet_id, 'rt':True, 'args': ''}, callback)
        
    def set_favorite(self, tweet_id, callback):
        self.log.debug('Marcando como favorito tweet: %s' % tweet_id)
        self.__register({'uri': 'http://twitter.com/favorites/create', 'id':tweet_id, 'fav': True, 'args': ''}, callback)
        
    def unset_favorite(self, tweet_id, callback):
        self.log.debug('Desmarcando como favorito tweet: %s' % tweet_id)
        self.__register({'uri': 'http://twitter.com/favorites/destroy', 'id':tweet_id, 'fav': False, 'args': ''}, callback)
    
    def search_topic(self, query, callback):
        args = {'q': query, 'rpp': 50}
        self.log.debug('Buscando tweets: %s' % query)
        self.__register({'uri': 'http://search.twitter.com/search', 'args': args}, callback)
        
    def end_session(self):
        self.__register({'uri': 'http://twitter.com/account/end_session', 'args': '', 'exit': True}, None)
        
    def quit(self):
        self.exit = True
        
    def run(self):
        while not self.exit:
            try:
                req = self.queue.get(False)
            except Queue.Empty:
                continue
            
            (args, callback) = req
            
            if args.has_key('oauth'):
                self.__handle_oauth(args, callback)
                continue
            
            rtn = None
            argStr = ""
            argData = None
            encoded_args = None
            method = "GET"
            uri = args['uri']
                
            for action in POST_ACTIONS:
                if uri.endswith(action): method = "POST"
            
            if args.has_key('id'):
                uri = "%s/%s" % (uri, args['id'])
                
            uri = "%s.%s" % (uri, self.format)
            
            if args.has_key('args'):
                encoded_args = urlencode(args['args'])
            
            if (method == "GET"):
                if encoded_args: argStr = "?%s" %(encoded_args)
            else:
                argData = encoded_args
                
            if self.is_oauth:
                try:
                    params = args['args'] if args.has_key('args') else {}
                    oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.token, http_method=method, http_url=uri, parameters=params)
                    oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, self.token)
                    rtn = json.loads(self.client.access_resource(oauth_request, uri, method))
                    #if rtn.has_key('error'): rtn = None
                except Exception, e:
                    self.log.debug("Error for URL: %s using parameters: (%s)\ndetails: %s" % (
                        uri, params, traceback.print_exc()))
                    if args.has_key('login'): 
                        rtn = {'error': 'Error from Twitter.com'}
            else:
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
                if rtn: self.tweets = rtn
            elif args.has_key('replies'):
                if rtn: self.replies = rtn
            elif args.has_key('favorites'):
                if rtn: self.favorites = rtn
                
            if args.has_key('tweet'):
                done = self.__handle_tweets(rtn, args)
                if done: rtn = self.__handle_muted()
            
            if args.has_key('rt'):
                done = self.__handle_retweets(rtn)
                if done: 
                    rtn = self.__handle_muted()
                    callback(rtn, self.replies, self.favorites)
                else:
                    callback(None, None, None)
                continue
                
            if args.has_key('fav'):
                done = self.__handle_favorites(rtn, args['fav'])
                if done: 
                    rtn = self.__handle_muted()
                    callback(rtn, self.replies, self.favorites)
                else:
                    callback(None, None, None)
                continue
                
            if args.has_key('exit'):
                self.exit = True
            else:
                callback(rtn)
            
        self.log.debug('Terminado')
        return

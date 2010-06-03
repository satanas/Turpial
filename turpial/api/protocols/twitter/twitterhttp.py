# -*- coding: utf-8 -*-

"""Implementación del módulo para peticiones HTTP adaptado a Twitter"""
#
# Author: Wil Alvarez (aka Satanas)
# May 26, 2010

import urllib2
import logging
import traceback

from turpial.api.protocols.twitter.oauth_client import TurpialAuthClient
from turpial.api.interfaces.http import TurpialHTTP, TurpialException
from turpial.api.protocols.twitter.twitter_globals import POST_ACTIONS

class TwitterHTTP(TurpialHTTP):
    def __init__(self):
        TurpialHTTP.__init__(self, POST_ACTIONS)
        self.log = logging.getLogger('TwitterHTTP')
        self.oauth_support = False
        
    def xauth(self, username, password, auth):
        '''Estableciendo credenciales'''
        self.username = username
        self.password = password
        
        self.client = TurpialAuthClient()
        
        if auth['oauth-key'] != '' and auth['oauth-secret'] != '':
            self.token = self.client.build_access_token(auth['oauth-key'], 
                auth['oauth-secret'])
            self.oauth_support = True
            
            return (self.token.key, self.token.secret)
        else:
            try:
                self.token = self.client.fetch_xauth_access_token(username, password)
                self.log.debug('GOT')
                self.log.debug('key: %s' % str(self.token.key))
                self.log.debug('secret: %s' % str(self.token.secret))
                self.oauth_support = True
                
                return (self.token.key, self.token.secret)
            except Exception, exc:
                self.log.debug("Auth error: %s" % (traceback.print_exc()))
                raise TurpialException('Authentication Error')
        
    def _simple_request(self, url, args={}):
        req = self._build_request(url, args)
        return self._execute_simple_request(req)
        
    def _secure_request(self, url, params={}):
        req = self._build_request(url, params)
        req.headers = self.client.apply_auth(req, params)
        #rtn = self.client.access_resource(url, req.method, params)
        rtn = self._execute_simple_request(req)
        print 'secure:', rtn
        return self._load_json(rtn)
        
    def request(self, uri, args={}):
        try:
            if self.oauth_support:
                rtn = self._secure_request(uri, args)
            else:
                rtn = self._simple_request(uri, args)
            return rtn
        except urllib2.HTTPError, exc:
            self.log.debug("HTTPError for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            if (exc.code == 304):
                return []
            elif (exc.code == 400):
                #X-RateLimit-Remaining
                raise TurpialException('You don\'t have more API calls')
            elif (exc.code == 401):
                raise TurpialException('Invalid username/password')
            elif (exc.code == 403):
                raise TurpialException('Hey! You are over the limit of API calls')
            elif (exc.code == 404):
                raise TurpialException('Err... invalid request')
            elif (exc.code == 406):
                raise TurpialException('You are searching a very weird thing')
            elif (exc.code == 420):
                raise TurpialException('You are searching too much!')
            elif (exc.code == 500):
                raise TurpialException('Oops! Something went wrong')
            elif (exc.code == 502):
                raise TurpialException('Twitter is down. Try again later')
            elif (exc.code == 503):
                raise TurpialException('Twitter is overcapacity')
        except urllib2.URLError, exc:
            self.log.debug("URLError for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            raise TurpialException('Can\'t connect to Twitter')
        except Exception, exc:
            self.log.debug("Unknown error for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            raise TurpialException(exc)

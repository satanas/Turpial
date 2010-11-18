# -*- coding: utf-8 -*-

"""Implementación del módulo para peticiones HTTP adaptado a Twitter"""
#
# Author: Wil Alvarez (aka Satanas)
# May 26, 2010

import urllib2
import logging
import traceback

from turpial.api.protocols.twitter import oauth
from turpial.api.interfaces.http import TurpialHTTP, TurpialException
from turpial.api.protocols.twitter.globals import POST_ACTIONS
from turpial.api.protocols.twitter.globals import CONSUMER_KEY, CONSUMER_SECRET


class TwitterHTTP(TurpialHTTP):
    def __init__(self):
        TurpialHTTP.__init__(self, POST_ACTIONS)
        self.log = logging.getLogger('TwitterHTTP')
        self.access_url = 'https://api.twitter.com/oauth/access_token'
        
        self.token = None
        self.consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        self.sign_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        
    def __fetch_xauth_access_token(self, username, password):
        request = oauth.OAuthRequest.from_consumer_and_token(
            oauth_consumer=self.consumer,
            http_method='POST', http_url=self.access_url,
            parameters = {
                'x_auth_mode': 'client_auth',
                'x_auth_username': username,
                'x_auth_password': password
            }
        )
        request.sign_request(self.sign_method_hmac_sha1, self.consumer, None)

        req = urllib2.Request(self.access_url, data=request.to_postdata())
        response = urllib2.urlopen(req)
        self.token = oauth.OAuthToken.from_string(response.read())
        return self.token
        
    def apply_auth(self, httpreq):
        request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
            token=self.token, http_method=httpreq.method, http_url=httpreq.uri,
            parameters=httpreq.params)
        request.sign_request(self.sign_method_hmac_sha1,
            self.consumer, self.token)
        httpreq.headers.update(request.to_header())
        
        return httpreq
            
    def auth(self, username, password):
        '''Estableciendo credenciales'''
        self.username = username
        self.password = password
        
        try:
            self.token = self.__fetch_xauth_access_token(username, password)
            
            return (self.token.key, self.token.secret)
        except Exception, exc:
            self.log.debug("Auth error: %s" % (traceback.print_exc()))
            raise TurpialException(_('Authentication Error'))
        
    def request(self, uri, args={}):
        try:
            rtn = self.do_request(uri, args)
            return rtn
        except urllib2.HTTPError, exc:
            self.log.debug("HTTPError for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            if (exc.code == 304):
                return []
            elif (exc.code == 400):
                #X-RateLimit-Remaining
                raise TurpialException(_('Sorry, you don\'t have more API \
calls'))
            elif (exc.code == 401):
                raise TurpialException(_('Invalid credentials'))
            elif (exc.code == 403):
                rtn = exc.read()
                print 'Error 403:', rtn
                if rtn.find("Status is a duplicate.") > 0:
                    msg = _('Your status was sent. Don\'t try again')
                elif rtn.find("is already on your list.") > 0:
                    msg = _('%s already is a friend')
                elif rtn.find("already requested to follow") > 0:
                    msg = _('You\'ve already requested to follow %s')
                else:
                    msg = _('Hey! You are over the limit of API calls')
                raise TurpialException(msg)
            elif (exc.code == 404):
                raise TurpialException(_('Err... invalid request'))
            elif (exc.code == 406):
                raise TurpialException(_('You are searching a very weird thing'))
            elif (exc.code == 420):
                raise TurpialException(_('You are searching too much!'))
            elif (exc.code == 500):
                raise TurpialException(_('Oops! Something went wrong'))
            elif (exc.code == 502):
                raise TurpialException(_('Twitter is down. Try again later'))
            elif (exc.code == 503):
                raise TurpialException(_('Twitter is overcapacity'))
        except urllib2.URLError, exc:
            self.log.debug("URLError for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            raise TurpialException(_('Can\'t connect to Twitter'))
        except Exception, exc:
            self.log.debug("Unknown error for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            raise TurpialException(exc)

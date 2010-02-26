# -*- coding: utf-8 -*-

# Modelo para solicitudes HTTP de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Feb 14, 2010

import oauth
import urllib2

from base64 import b64encode
from urllib import urlencode

from twitter_globals import *
from oauth_client import TurpialAuthClient

def _py26OrGreater():
    import sys
    return sys.hexversion > 0x20600f0

if _py26OrGreater():
    import json
else:
    import simplejson as json

class TurpialHTTP:
    def __init__(self):
        # OAuth stuffs
        self.format = 'json'
        self.username = None
        self.password = None
        self.client = None
        self.consumer = None
        self.is_oauth = False
        self.token = None
        self.signature_method_hmac_sha1 = None
        
    def set_credentials(self, username, password):
        self.username = username
        self.password = password
        
    def request(self, args)
        rtn = None
        encoded_args = None
        
        argStr = ""
        argData = None
        uri = args['uri']
        method = "GET"
        response = ''
        
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
            
        try:
            if self.is_oauth:
                argData = args['args'] if args.has_key('args') else {}
                oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, token=self.token, http_method=method, http_url=uri, parameters=argData)
                oauth_request.sign_request(self.signature_method_hmac_sha1, self.consumer, self.token)
                response = self.client.access_resource(oauth_request, uri, method)
                rtn = json.loads(response)
            else:
                headers = {}
                if (self.username):
                    headers["Authorization"] = "Basic " + b64encode("%s:%s" %(self.username, self.password))
                req = urllib2.Request("%s%s" %(uri, argStr), argData, headers)
                handle = urllib2.urlopen(req)
                response = handle.read()
                rtn = json.loads(response)
                
        except urllib2.HTTPError, e:
            if (e.code == 304):
                rtn = []
            else:
                error_msg = "Error %i from twitter.com\n" + 
                    "Details: %s\nRequest: %s\nMethod: %s\nargStr: %s\n" + 
                    "argData: %s\nResponse: %s\n"
                self.log.debug(error_msg % (e.code, e, uri, method, argStr, argData, response))
            
            if args.has_key('login'): 
                rtn = {'error': 'Error %i from Twitter.com' % e.code}
        except (urllib2.URLError, Exception), e:
            error_msg = "Problem to connect to twitter.com\n" + 
                "Details: %s\nRequest: %s\nMethod: %s\nargStr: %s\n" + 
                "argData: %s\nResponse: %s\n"
            self.log.debug(error_msg %(e, uri, method, argStr, argData, response))
            if args.has_key('login'): 
                rtn = {'error': 'Can\'t connect to twitter.com'}
        
        return rtn
        
    def oauth(self, args, callback):
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
                try:
                    self.token = self.client.fetch_request_token(oauth_request)
                except Exception, e:
                    print "Error: %s\n%s" % (e, traceback.print_exc())
                    raise Exception
                
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

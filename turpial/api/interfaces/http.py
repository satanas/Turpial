# -*- coding: utf-8 -*-

"""Módulo genérico para manejar las solicitudes HTTP de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import urllib2
import logging

from base64 import b64encode
from urllib import urlencode

def _py26_or_greater():
    import sys
    return sys.hexversion > 0x20600f0

if _py26_or_greater():
    import json
else:
    import simplejson as json

class TurpialHTTP:
    def __init__(self, post_actions):
        self.format = 'json'
        self.post_actions = post_actions
        self.username = None
        self.password = None
        self.log = logging.getLogger('TurpialHTTP')
        
    def _simple_request(self, uri, args={}):
        ''' Reimplement in child class '''
        try:
            req = self._build_request(uri, args)
            rtn = self._execute_simple_request(req)
            return rtn
        except Exception, e:
            raise TurpialException(e)
        
    def _build_request(self, uri, args={}):
        argStr = ''
        headers = {}
        response = ''
        argData = None
        encoded_args = ''
        method = "GET"
            
        for action in self.post_actions:
            if uri.endswith(action):
                method = "POST"
                break
        
        if args.has_key('id'):
            uri = "%s/%s" % (uri, args['id'])
            del args['id']
        
        uri = "%s.%s" % (uri, self.format)
        self.log.debug('URI: %s' % uri)
        
        if len(args) > 0:
            encoded_args = urlencode(args)
        
        if method == "GET":
            if encoded_args:
                argStr = "?%s" % (encoded_args)
        else:
            argData = encoded_args
            
        if (self.username):
            auth_info = b64encode("%s:%s" % (self.username, self.password))
            headers["Authorization"] = "Basic " + auth_info
        
        strReq = "%s%s" % (uri, argStr)
        #print "%s-%s-%s-%s-%s-%s-" % (method, encoded_args, argStr, argData, headers, strReq)
        #req = urllib2.Request(strReq, argData, headers)
        req = TurpialHTTPRequest(argStr, headers, argData, encoded_args, 
            method, strReq, uri)
        return req
    
    def _execute_simple_request(self, httpreq):
        req = urllib2.Request(httpreq.strReq, httpreq.argData, httpreq.headers)
        handle = urllib2.urlopen(req)
        return self._load_json(handle.read())
        
    def _load_json(self, response):
        return json.loads(response)
        
    def set_credentials(self, username, password):
        '''Estableciendo credenciales'''
        self.username = username
        self.password = password
        
    def request(self, url, args={}):
        return self._simple_request(url, args)
        
class TurpialHTTPRequest:
    def __init__(self, argStr='', headers={}, argData=None, encoded_args='', 
        method="GET", strReq='', uri=''):
        
        self.argStr = argStr
        self.headers = headers
        self.argData = argData
        self.encoded_args = encoded_args
        self.method = method
        self.strReq = strReq
        self.uri = uri
        
class TurpialException(Exception):
    def __init__(self, msg):
       self.msg = msg
       
    def __str__(self):
       return repr(self.msg)
       

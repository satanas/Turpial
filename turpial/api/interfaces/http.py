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
        self.username = None
        self.password = None
        self.post_actions = post_actions
        self.log = logging.getLogger('TurpialHTTP')
        
    def __build(self, uri, args={}):
        '''Construir la petición HTTP'''
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
        
        strReq = "%s%s" % (uri, argStr)
        req = TurpialHTTPRequest(argStr, headers, argData, encoded_args, 
            method, strReq, uri, args)
        return req
    
    def __send(self, httpreq):
        req = urllib2.Request(httpreq.strReq, httpreq.argData, httpreq.headers)
        handle = urllib2.urlopen(req)
        return json.loads(handle.read())
        
    def _basic_auth(self, httpreq):
        if self.username and httpreq.method == 'POST':
            auth_info = b64encode("%s:%s" % (self.username, self.password))
            httpreq.headers["Authorization"] = "Basic " + auth_info
        return httpreq
            
    def apply_auth(self, httpreq):
        '''Autenticación para las peticiones. Reimplementar si hace falta'''
        return self._basic_auth(httpreq)
        
    def auth(self, username, password, data):
        '''Estableciendo credenciales'''
        self.username = username
        self.password = password
        
    def do_request(self, url, args={}):
        ''' Realizado una petición HTTP'''
        # Construir la petición
        httpreq = self.__build(url, args)
        # Autenticarla si es necesario
        authreq = self.apply_auth(httpreq)
        # Enviarla y obtener la respuesta
        response = self.__send(authreq)
        return response
        
    def request(self, url, args={}):
        '''Send the request to server. Implement it using a call to 'do_request'
        and making all needs validations'''
        raise NotImplemented
    
class TurpialHTTPRequest:
    def __init__(self, argStr='', headers={}, argData=None, encoded_args='', 
        method="GET", strReq='', uri='', params={}):
        
        self.argStr = argStr
        self.headers = headers
        self.argData = argData
        self.encoded_args = encoded_args
        self.method = method
        self.strReq = strReq
        self.params = params
        self.uri = uri
        
    def __str__(self):
        return "method: %s\nencoded_args: %s\nargStr: %s\nargData: %s\n\
headers: %s\nstrReq: %s-" % (self.method, self.encoded_args, 
            self.argStr, self.argData, self.headers, self.strReq)
        
class TurpialException(Exception):
    def __init__(self, msg):
       self.msg = msg
       
    def __str__(self):
       return repr(self.msg)
       

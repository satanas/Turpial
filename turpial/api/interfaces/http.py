# -*- coding: utf-8 -*-

"""Módulo genérico para manejar las solicitudes HTTP de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import os
import socket
import urllib2
import urllib
import httplib
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
    
try:
    import gconf
    GCONF = True
except:
    GCONF = False
    
def detect_desktop_environment():
    desktop_environment = 'generic'
    if os.environ.get('KDE_FULL_SESSION') == 'true':
        desktop_environment = 'kde'
    elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
        desktop_environment = 'gnome'
    # FIXME: Deshabilitado temporalmente mientras se encuentra una forma de 
    # detectar otros tipos de escritorios
    '''
    else:
        try:
            info = getoutput('xprop -root _DT_SAVE_MODE')
            if ' = "xfce4"' in info:
                desktop_environment = 'xfce'
        except (OSError, RuntimeError):
            pass
    '''
    return desktop_environment

class TurpialHTTP:
    def __init__(self, post_actions):
        self.format = 'json'
        self.username = None
        self.password = None
        self.post_actions = post_actions
        self.log = logging.getLogger('TurpialHTTP')
        
        # timeout in seconds
        timeout = 20
        socket.setdefaulttimeout(timeout)
        proxies = {}
        
        if detect_desktop_environment() == 'gnome' and GCONF:
            gclient = gconf.client_get_default()
            if gclient.get_bool('/system/http_proxy/use_http_proxy'):
                proxies['http'] = "%s:%d" % (
                    gclient.get_string('/system/http_proxy/host'), 
                    gclient.get_int('/system/http_proxy/port'))
                if gclient.get_bool('/system/http_proxy/use_same_proxy'):
                    proxies['https'] = proxies['http']
                elif gclient.get_string('/system/proxy/secure_host'):
                    proxies['https'] = "%s:%d" % (
                        gclient.get_string('/system/http/secure_host'), 
                        gclient.get_int('/system/proxy/secure_port'))
            
            if proxies:
                self.log.debug('Proxies detectados: %s' % proxies)
                if proxies.has_key('https'):
                    opener = urllib2.build_opener(ConnectHTTPSHandler(proxy=proxies['https']))
                    urllib2.install_opener(opener)
                else:
                    opener = urllib2.build_opener(ConnectHTTPSHandler(proxy=proxies['http']))
                    urllib2.install_opener(opener)
            else:
                self.log.debug('No se detectarion proxies en el sistema')
        
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
        if self.username:
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
        
class ProxyHTTPConnection(httplib.HTTPConnection):

    _ports = {'http' : 80, 'https' : 443}


    def request(self, method, url, body=None, headers={}):
        #request is called before connect, so can interpret url and get
        #real host/port to be used to make CONNECT request to proxy
        proto, rest = urllib.splittype(url)
        if proto is None:
            raise ValueError, "unknown URL type: %s" % url
        #get host
        host, rest = urllib.splithost(rest)
        #try to get port
        host, port = urllib.splitport(host)
        #if port is not defined try to get from proto
        if port is None:
            try:
                port = self._ports[proto]
            except KeyError:
                raise ValueError, "unknown protocol for: %s" % url
        self._real_host = host
        self._real_port = port
        httplib.HTTPConnection.request(self, method, url, body, headers)
        

    def connect(self):
        httplib.HTTPConnection.connect(self)
        #send proxy CONNECT request
        self.send("CONNECT %s:%d HTTP/1.0\r\n\r\n" % (self._real_host, self._real_port))
        #expect a HTTP/1.0 200 Connection established
        response = self.response_class(self.sock, strict=self.strict, method=self._method)
        (version, code, message) = response._read_status()
        #probably here we can handle auth requests...
        if code != 200:
            #proxy returned and error, abort connection, and raise exception
            self.close()
            raise socket.error, "Proxy connection failed: %d %s" % (code, message.strip())
        #eat up header block from proxy....
        while True:
            #should not use directly fp probablu
            line = response.fp.readline()
            if line == '\r\n': break


class ProxyHTTPSConnection(ProxyHTTPConnection):
    
    default_port = 443

    def __init__(self, host, port = None, key_file = None, cert_file = None, strict = None):
        ProxyHTTPConnection.__init__(self, host, port)
        self.key_file = key_file
        self.cert_file = cert_file
    
    def connect(self):
        ProxyHTTPConnection.connect(self)
        #make the sock ssl-aware
        ssl = socket.ssl(self.sock, self.key_file, self.cert_file)
        self.sock = httplib.FakeSocket(self.sock, ssl)
        
                                       
class ConnectHTTPHandler(urllib2.HTTPHandler):

    def __init__(self, proxy=None, debuglevel=0):
        self.proxy = proxy
        urllib2.HTTPHandler.__init__(self, debuglevel)

    def do_open(self, http_class, req):
        if self.proxy is not None:
            req.set_proxy(self.proxy, 'http')
        return urllib2.HTTPHandler.do_open(self, ProxyHTTPConnection, req)

class ConnectHTTPSHandler(urllib2.HTTPSHandler):

    def __init__(self, proxy=None, debuglevel=0):
        self.proxy = proxy
        urllib2.HTTPSHandler.__init__(self, debuglevel)

    def do_open(self, http_class, req):
        if self.proxy is not None:
            req.set_proxy(self.proxy, 'https')
        return urllib2.HTTPSHandler.do_open(self, ProxyHTTPSConnection, req)
        
class TurpialException(Exception):
    def __init__(self, msg):
       self.msg = msg
       
    def __str__(self):
       return repr(self.msg)
       

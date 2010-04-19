# -*- coding: utf-8 -*-

"""Módulo genérico para manejar los servicios en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 18, 2010

import os
import urllib2
import logging

def _py26_or_greater():
    import sys
    return sys.hexversion > 0x20600f0
    
if _py26_or_greater():
    import json
else:
    import simplejson as json

class GenericService:
    def __init__(self):
        self.log = logging.getLogger('Service')
        
    @staticmethod
    def _download_pic(imgdir, fileurl):
        ''' Download an image file from it URL '''
        #self.log.debug('Downloading Pic: %s' % fileurl)
        
        ext = fileurl[-3:]
        if ext == '':
            ext = 'png'
        filename = fileurl.replace('http://', '0_')
        filename = filename.replace('/', '_')
        fullname = os.path.join(imgdir, filename)
        
        picdata = urllib2.urlopen(fileurl).read()
        
        _file = open(fullname, 'w+')
        _file.write(picdata)
        _file.close()
        
        return filename
        
    def _get_request(self, url, data=None):
        ''' Process a GET request and returns a text plain response '''
        self.log.debug('GET Request: %s' % url)
        return urllib2.urlopen(url, data).read()
        
    def _json_request(self, url):
        ''' Process a GET request and returns a json hash '''
        self.log.debug('JSON Request: %s' % url)
        return json.loads(urllib2.urlopen(url).read())
        
    def _quote_url(self, url):
        longurl = urllib2.quote(url)
        longurl = longurl.replace('/', '%2F')
        return longurl
        
    def do_service(self, arg):
        raise NotImplemented
        
class ServiceResponse:
    def __init__(self, response=None, err=False, err_msg=None):
        self.response = response
        self.err = err
        self.err_msg = err_msg

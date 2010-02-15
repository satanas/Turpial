# -*- coding: utf-8 -*-

# Modelo base basado en hilos para el Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 22, 2009

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2

import traceback

#URL_UPLOAD = 'http://twitpic.com/api/uploadAndPost'
URL_UPLOAD = 'http://twitpic.com/api/upload'

class TwitPicAPI(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def upload(self, image, message=''):
        try:
            register_openers()
            datagen, headers = multipart_encode({
                "media": open(image),
                "username": self.username, 
                "password": self.password, 
                "message": message,
            })
                
            # Create the Request object
            request = urllib2.Request(URL_UPLOAD, datagen, headers)
            # Actually do the request, and get the response
            response = urllib2.urlopen(request).read()
            return self.parse_xml('mediaurl',response)
        
        except Exception, e:
            print e, traceback.print_exc()
            return None
            
    def parse_xml(self,key,xml):
        """ Simple XML parser """
        key = key.lower()
        for tag in xml.split("<"):
            tokens = tag.split()
            if tokens and tokens[0].lower().startswith(key):
                return tag.split(">")[1].strip()

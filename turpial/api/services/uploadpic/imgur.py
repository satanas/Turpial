# -*- coding: utf-8 -*-

"""Interfaz para imgur en Turpial"""
#
# Author: Efrain Valles 
# Oct 10, 2011

import os
import httplib
import traceback
import pycurl
import base64
import urllib

def _py26_or_greater():
    import sys
    return sys.hexversion > 0x20600f0

if _py26_or_greater():
    import json
else:
    import simplejson as json


from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse
from turpial.api.interfaces.http import TurpialHTTPRequest

IMGUR_KEY = '710afc95df6a25864a9f7df6b6a0b103'

class ImgurPicUploader(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.server = "api.imgur.com"
        self.base = "/2/upload.json"
        self.provider = 'https://api.twitter.com/1/account/verify_credentials.xml'
        
    def do_service(self, username, password, filepath, message, httpobj):
        try:
            _image = self._open_file(filepath)
        except:
            return self._error_opening_file(filepath)
        
        postdata = {"key": IMGUR_KEY,
		    "image":base64.b64encode(_image),
		    "caption":message,}
	data = urllib.urlencode(postdata)
        try:
            resp = urllib.urlopen("http://api.imgur.com/2/upload.json",data)
            resp_json = json.loads(resp.read())
            link = resp_json['upload']['links'].get('imgur_page')
            print link
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))

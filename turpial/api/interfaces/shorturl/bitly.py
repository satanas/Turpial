# -*- coding: utf-8 -*-

"""Interfaz para bit.ly en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import urllib2
import traceback

from turpial.api.interfaces.generic import GenericService
from turpial.api.interfaces.generic import ServiceResponse

APIKEY = 'apiKey=R_5a84eae6dd4158a0636358c4f9efdecc'
VERSION = 'version=2.0.1'
APP = 'login=turpial'

class BitlyURLShorter(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.base = "http://api.bit.ly/shorten?%s&%s&%s&longUrl=%s"
        
    def do_service(self, keyurl):
        longurl = self._quote_url(keyurl)
        req = self.base % (VERSION, APP, APIKEY, longurl)
        try:
            resp = self._json_request(req)
            return ServiceResponse(resp['results'][keyurl]['shortUrl'])
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem shorting URL'))
        

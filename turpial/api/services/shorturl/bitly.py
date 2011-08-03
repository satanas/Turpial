# -*- coding: utf-8 -*-

"""Interfaz para bit.ly en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import traceback

from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse

LOGIN = 'login=turpial'
APIKEY = 'apiKey=R_5a84eae6dd4158a0636358c4f9efdecc'

class BitlyURLShorter(GenericService):
    def __init__(self, domain='bit.ly'):
        GenericService.__init__(self)
        self.base = 'http://api.bitly.com/v3/shorten?domain=%s' % domain # shorten?%s&%s&%s&longUrl=%s&domain=" + domain
        
    def do_service(self, keyurl):
        longurl = 'longurl=%s' % self._quote_url(keyurl)
        req = '%s&%s' % (self.base, '&'.join([LOGIN, APIKEY, longurl]))
        try:
            resp = self._json_request(req)
            return ServiceResponse(resp['data']['url'])
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem shorting URL'))
        

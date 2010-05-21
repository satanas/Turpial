# -*- coding: utf-8 -*-

"""Interfaz para smlk.es en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import urllib2
import traceback

from turpial.api.interfaces.generic import GenericService
from turpial.api.interfaces.generic import ServiceResponse

class SmlkesURLShorter(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.base = "http://smlk.es/api/create/?destination=%s"
        
    def do_service(self, keyurl):
        longurl = self._quote_url(keyurl)
        req = self.base % longurl
        try:
            resp = self._json_request(req)
            #print resp
            short = "http://smlk.es/%s" % resp['link']
            return ServiceResponse(short)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem shorting URL'))
        

# -*- coding: utf-8 -*-

"""Interfaz para goo.gl en Turpial"""

import traceback

from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse

class GooglURLShorter(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.url = "http://goo.gl/api/url"
        
    def do_service(self, longurl):
        longurl = self._quote_url(longurl)
        data = "url=%s" % longurl
        try:
            resp = self._json_request(self.url, data)
            return ServiceResponse(resp['short_url'])
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem shorting URL'))
        

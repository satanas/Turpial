# -*- coding: utf-8 -*-

"""Interfaz para ur1.ca en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import re
import urllib
import traceback

from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse

class Ur1caURLShorter(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.base = "http://ur1.ca"
        self.pt = re.compile('<p class="success">Your ur1 is: <a href="(.*?)">')

    def do_service(self, longurl):
        values = {'submit' : 'Make it an ur1!', 'longurl' : longurl}
        
        try:
            data = urllib.urlencode(values)
            resp = self._get_request(self.base, data)
            short = self.pt.findall(resp)
            
            if len(short) > 0:
                return ServiceResponse(short[0])
            else:
                raise Exception
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem shorting URL'))

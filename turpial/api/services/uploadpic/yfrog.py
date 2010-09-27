# -*- coding: utf-8 -*-

"""Interfaz para yfrog en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import httplib
import traceback

from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse
from turpial.api.interfaces.http import TurpialHTTPRequest

YFROG_KEY = '189ACHINb967317adad418caebd9a22615d00cb7'

class YfrogPicUploader(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.server = "yfrog.com"
        self.base = "/api/xauth_upload"
        self.provider = 'https://api.twitter.com/1/account/verify_credentials.xml'
        
    def do_service(self, username, password, filepath, httpobj):
        _file = open(filepath, 'r')
        files = (
            ('media', self._get_pic_name(filepath), _file.read()),
        )
        _file.close()
        
        fields = (
            ('key', YFROG_KEY),
        )
        try:
            resp = self._upload_pic(self.server, self.base, fields, files, httpobj)
            print resp
            link = self._parse_xml('mediaurl', resp)
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))

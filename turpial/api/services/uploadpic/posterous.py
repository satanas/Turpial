# -*- coding: utf-8 -*-

"""Interfaz para Posterous en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Sep 27, 2010

import traceback

from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse

class PosterousPicUploader(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.server = "posterous.com"
        self.base = "/api2/upload.xml"
        self.provider = 'https://api.twitter.com/1/account/verify_credentials.json'
        
    def do_service(self, username, password, filepath, httpobj):
        _file = open(filepath, 'r')
        files = (
            ('media', self._get_pic_name(filepath), _file.read()),
        )
        _file.close()
        
        fields = ()
        
        try:
            resp = self._upload_pic(self.server, self.base, fields, files, httpobj)
            link = self._parse_xml('url', resp)
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))

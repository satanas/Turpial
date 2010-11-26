# -*- coding: utf-8 -*-

"""Interfaz para Twitpic en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import traceback

from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse

TWITPIC_KEY = '57d17b42f1001ffc64bf22ceef98968d'

class TwitpicPicUploader(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.server = "api.twitpic.com"
        self.base = "/2/upload.xml"
        self.provider = 'https://api.twitter.com/1/account/verify_credentials.json'
        
    def do_service(self, username, password, filepath, message, httpobj):
        try:
            _image = self._open_file(filepath)
        except:
            return self._error_opening_file(filepath)
        
        files = (
            ('media', self._get_pic_name(filepath), _image),
        )
        
        fields = (
            ('key', TWITPIC_KEY),
            ('message', message),
        )
        try:
            resp = self._upload_pic(self.server, self.base, fields, files, httpobj)
            link = self._parse_xml('url', resp)
            #print resp, link
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))

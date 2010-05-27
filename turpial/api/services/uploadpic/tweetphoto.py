# -*- coding: utf-8 -*-

"""Interfaz para tweetphoto.com en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import traceback

from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse

TWEETPHOTO_KEY = '09e874f8-a7ed-4ae4-a810-3cf7040b9c40'

class TweetPhotoPicUploader(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.server = "tweetphotoapi.com"
        self.base = "/api/upload.aspx"
        
    def do_service(self, username, password, filepath):
        _file = open(filepath, 'r')
        files = (
            ('media', self._get_pic_name(filepath), _file.read()),
        )
        _file.close()
        
        fields = (
            ('username', username),
            ('password', password),
            ('api_key', TWEETPHOTO_KEY),
        )
        try:
            resp = self._upload_pic(self.server, self.base, fields, files)
            link = self._parse_xml('MediaUrl', resp)
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))

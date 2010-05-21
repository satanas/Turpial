# -*- coding: utf-8 -*-

"""Interfaz para Mobypicture en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import traceback

from turpial.api.interfaces.generic import GenericService
from turpial.api.interfaces.generic import ServiceResponse

KEY = 'uF6kIJuyGGKsol8i'

class MobypicturePicUploader(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.server = "api.mobypicture.com"
        self.base = "/"
        
    def do_service(self, username, password, filepath):
        _file = open(filepath, 'r')
        files = (
            ('i', self._get_pic_name(filepath), _file.read()),
        )
        _file.close()
        
        fields = (
            ('u', username),
            ('p', password),
            ('action', 'postMediaUrl'),
            ('format', 'xml'),
            ('k', KEY),
        )
        try:
            resp = self._upload_pic(self.server, self.base, fields, files)
            link = self._parse_xml('url', resp)
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))

# -*- coding: utf-8 -*-

"""Interfaz para tweetphoto.com en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import logging
import traceback

from turpial.api.interfaces.http import TurpialHTTPRequest
from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse
from turpial.api.services.uploadpic.pyTweetPhoto import TweetPhotoApi

TWEETPHOTO_KEY = '09e874f8-a7ed-4ae4-a810-3cf7040b9c40'

class TweetPhotoPicUploader(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        self.log = logging.getLogger('Service')
        self.provider = 'https://api.twitter.com/1/account/verify_credentials.xml'
        
    def do_service(self, username, password, filepath, message, httpobj):
        try:
            _image = self._open_file(filepath)
        except:
            return self._error_opening_file(filepath)
            
        try:
            httpobj.change_format('xml')
            httpreq = TurpialHTTPRequest(method='GET', uri=self.provider)
            httpresp = httpobj.apply_auth(httpreq)
            auth_head = httpresp.headers['Authorization']
            auth_head = auth_head.replace('OAuth realm=""', 
                'OAuth realm="http://api.twitter.com/"')
            
            headers = {
                'X-Verify-Credentials-Authorization': auth_head,
                'X-Auth-Service-Provider': self.provider
            }
            
            httpobj.change_format('json')
            
            api = TweetPhotoApi(username, password, TWEETPHOTO_KEY)
            resp = api.Upload(fileName=filepath, image=_image, message=message,
                headers=headers)
            
            link = self._parse_xml('MediaUrl', resp)
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))


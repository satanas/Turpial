# -*- coding: utf-8 -*-

"""Interfaz para Twitpic en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 19, 2010

import httplib
import traceback

from turpial.api.protocols.twitter import oauth
from turpial.api.interfaces.http import TurpialHTTPRequest
from turpial.api.interfaces.service import GenericService
from turpial.api.interfaces.service import ServiceResponse
from turpial.api.protocols.twitter.globals import CONSUMER_KEY, CONSUMER_SECRET

TWITPIC_KEY = '57d17b42f1001ffc64bf22ceef98968d'

class TwitpicPicUploader(GenericService):
    def __init__(self):
        GenericService.__init__(self)
        
        self.server = "api.twitpic.com"
        self.base = "/2/upload.xml"
        self.service_provider = 'https://api.twitter.com/1/account/verify_credentials.json'
    
    def _upload_pic(self, host, upload_url, fields, files, httpobj):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be 
            uploaded as files
        Return the server's response page.
        """
        httpreq = TurpialHTTPRequest(method='GET', uri=self.service_provider)
        httpresp = httpobj.apply_auth(httpreq)
        auth_head = httpresp.headers['Authorization']
        auth_head = auth_head.replace('OAuth realm=""', 'OAuth realm="http://api.twitter.com/"')
        content_type, body = self._encode_multipart_formdata(fields, files)
        h = httplib.HTTPConnection(host)
        
        headers = {
            'User-Agent': 'Turpial',
            'X-Verify-Credentials-Authorization': auth_head,
            'X-Auth-Service-Provider': self.service_provider,
            'Content-Type': content_type
        }
        
        h.request('POST', upload_url, body, headers)
        res = h.getresponse()
        #return res.status, res.reason, res.read()
        return res.read()
        
    def do_service(self, username, password, filepath, httpobj):
        _file = open(filepath, 'r')
        files = (
            ('media', self._get_pic_name(filepath), _file.read()),
        )
        _file.close()
        
        fields = (
            ('key', TWITPIC_KEY),
        )
        try:
            resp = self._upload_pic(self.server, self.base, fields, files, httpobj)
            link = self._parse_xml('url', resp)
            #print resp, link
            return ServiceResponse(link)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem uploading pic'))

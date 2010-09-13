# -*- coding: utf-8 -*-

"""Módulo genérico para manejar los servicios en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Abr 18, 2010

import os
import httplib
import urllib2
import logging

def _py26_or_greater():
    import sys
    return sys.hexversion > 0x20600f0
    
if _py26_or_greater():
    import json
else:
    import simplejson as json

try:
    import mimetypes
    MIME_FLAG = True
except ImportError:
    MIME_FLAG = False

class GenericService:
    def __init__(self):
        self.log = logging.getLogger('Service')
        
    @staticmethod
    def _download_pic(imgdir, fileurl):
        ''' Download an image file from it URL '''
        #self.log.debug('Downloading Pic: %s' % fileurl)
        
        ext = fileurl[-3:]
        if ext == '':
            ext = 'png'
        filename = fileurl.replace('http://', '0_')
        filename = filename.replace('/', '_')
        fullname = os.path.join(imgdir, filename)
        
        picdata = urllib2.urlopen(fileurl).read()
        
        _file = open(fullname, 'w+')
        _file.write(picdata)
        _file.close()
        
        return filename
        
    def _get_request(self, url, data=None):
        ''' Process a GET request and returns a text plain response '''
        self.log.debug('GET Request: %s' % url)
        return urllib2.urlopen(url, data).read()
        
    def _json_request(self, url):
        ''' Process a GET request and returns a json hash '''
        self.log.debug('JSON Request: %s' % url)
        return json.loads(urllib2.urlopen(url).read())
        
    def _quote_url(self, url):
        longurl = urllib2.quote(url)
        longurl = longurl.replace('/', '%2F')
        return longurl
    
    def _upload_pic(self, host, upload_url, fields, files):
        """
        Post fields and files to an http host as multipart/form-data.
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be 
            uploaded as files
        Return the server's response page.
        """
        content_type, body = self._encode_multipart_formdata(fields, files)
        h = httplib.HTTPConnection(host)
        headers = {
            'User-Agent': 'Turpial',
            'Content-Type': content_type
        }
        h.request('POST', upload_url, body, headers)
        res = h.getresponse()
        #return res.status, res.reason, res.read()
        return res.read()
    
    def _encode_multipart_formdata(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        Return (content_type, body) ready for httplib.HTTP instance
        """
        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % self._get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
    
    def _get_content_type(self, filename):
        """Get the image content type"""
        if MIME_FLAG:
            return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        else:
            return 'image/jpg'
    
    def _get_pic_name(self, filepath):
        return os.path.split(filepath)[1]
            
    def _parse_xml(self, key, xml):
        """ Simple XML parser """
        key = key.lower()
        for tag in xml.split("<"):
            tokens = tag.split()
            if tokens and tokens[0].lower().startswith(key):
                return tag.split(">")[1].strip()
        
    def do_service(self, arg):
        raise NotImplementedError
        
class ServiceResponse:
    def __init__(self, response=None, err=False, err_msg=None):
        self.response = response
        self.err = err
        self.err_msg = err_msg

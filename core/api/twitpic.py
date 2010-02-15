# -*- coding: utf-8 -*-

# Modelo base basado en hilos para el Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 22, 2009

import httplib
import urllib

try:
    import mimetypes
    MIME_FLAG = True
except ImportError:
    MIME_FLAG = False

SERVER = 'twitpic.com'
UPLOAD_URL = '/api/uploadAndPost'
BLOCKSIZE = 8192

class TwitPicAPI(object):
    def __init__(self,username,password):
        self.username = username
        self.password = password
        self.filedata = None
        self.image = None
        self.connection = None
    
    def post_multipart(self, path, msg=''):
        '''
        fields = {'media': open(path, "rb"),
        'username': }
        media (required) - Binary image data
        - username (required) - Twitter username
        - password (required) - Twitter password
        - message (optional) - Message to post to twitter. The
        '''
        content_type, body = encode_multipart_formdata(fields, files)
        h = httplib.HTTPConnection(SERVER)
        headers = {
            'User-Agent': 'INSERT USERAGENTNAME',
            'Content-Type': content_type
            }
        h.request('POST', UPLOAD_URL, body, headers)
        res = h.getresponse()
        return res.read()
    
    def upload(self,image=None, message=None):
        self.image = image
        self.get_filedata()
        body_txt = self.filedata
        
        try:
            self.connection = httplib.HTTP(SERVER)
            self.connection.putrequest('POST', '/%s' % UPLOAD_URL)
            self.connection.putheader('content-type','multipart/form-data')
            self.connection.putheader('content-length', str(len(body_txt)))
            self.connection.endheaders()
        
            offs = 0
            for i in range(0, len(body_txt), BLOCKSIZE):
                offs += BLOCKSIZE
                self.connection.send(body_txt[i:offs])
        
            statusCode, statusMsg, headers = self.connection.getreply()
            response = self.connection.file.read()
                
            return self.parse_xml('mediaurl',response)
        
        except Exception, e:
            print e.fp.read()
            return None
            
            
    def encode_multipart_formdata(fields, files):
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
            L.append('Content-Type: %s' % get_content_type(filename))
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        return content_type, body
        
    def get_filedata(self):
        """ Method to get the image content in bytes
        """
        if self.filedata is None:
            self.filedata = file(self.image,'r').read()
        else:
            self.image = 'up.jpg'
            
    def get_content_type(self):
        """Get the image content type"""
        if MIME_FLAG:
            return mimetypes.guess_type(self.image)[0] or 'application/octet-stream'
        else:
            return 'image/jpg'
            
    def parse_xml(self,key,xml):
        """ Simple XML parser """
        key = key.lower()
        for tag in xml.split("<"):
            tokens = tag.split()
            if tokens and tokens[0].lower().startswith(key):
                return tag.split(">")[1].strip()

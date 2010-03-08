#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# s60tweetphoto - Simple TweetPhoto Module to Uploading photos for PyS60 apps

# Copyright (c) 2009, Marcel Caraciolo
# twitter: marcelcaraciolo
# http://mobideia.blogspot.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
__all__ = [ "TweetPhotoAPI" ]
__author__ = 'caraciol@gmail.com'
__version__ = '0.1'

import httplib, urllib

try:
    import mimetypes
    MIME_FLAG = True
except ImportError:
    MIME_FLAG = False

class TweetPhotoAPI(object):
    SERVER = 'tweetphotoapi.com'
    UPLOAD_URL = '/api/tpapi.svc/upload2'


    def __init__(self,username,password,apikey,image=None,filedata=None,
                    server=SERVER,upload_url = UPLOAD_URL):
        """Initializer of the TweetPhotoAPI, object that holds the TweetPhoto
            username/password/apiKey and server information. 
            Parameters:
                username: twitter username
                password: twitter password
                apikey: The TweetPhoto API Key. It can be acquired at http://tweetphoto.com/developer
                image: The path to the image
                filedata: the fileData image
                server: the SERVER url
                upload_url: the upload url
            """
        
        self.server = server
        self.username = username
        self.password = password
        self.apiKey = apikey
        self.filedata = filedata
        self.image = image
        self.upload_url = upload_url
        self.connection = None
                            

    def upload(self,image=None, message=None, tags=None, geoLocation=None,post_to_twitter = False):
        """ Method called to upload a photo to TweetPhoto Web Service
            Parameters:
                image: the Image Path
                message: the message for the photo, limited to 200 characters.
                tags: a comma delimited list of tags for the photo (e.g. 'cat,awesome,funny')'
                geoLocation: a string in the format lat,long with the geolocation tag for latitude and longitude
                post_to_twitter:  Whether or not to post to twitter.
            Return:
                If uploaded: the url media  else: the error code
        """
        
        BLOCKSIZE = 8192
        
        if image:
            self.image = image
        self.get_filedata()
                
                
        body_txt = self.filedata
        
                
        try:
            self.connection = httplib.HTTP(self.server)
            self.connection.putrequest('POST', '/%s' %self.upload_url)
            self.connection.putheader('content-type','application/x-www-form-urlencoded')
            self.connection.putheader('TPAPIKEY', self.apiKey)
            self.connection.putheader('TPAPI', self.username + ',' + self.password)
            self.connection.putheader('TPMIMETYPE', self.get_content_type())
        
            if post_to_twitter: #Default value is False
                self.connection.putheader('TPPOST', 'True')
            
            if message is not None: #Default value is Null
                self.connection.putheader('TPMSG', message)
        
            if tags is not None: #Default value is Null
                self.connection.putheader('TPTAGS',tags)
        
            if geoLocation is not None: #Default value is Null
                g = geoLocation.split(',')
                self.connection.putheader('TPLAT',g[0])
                self.connection.putheader('TPLONG', g[1])
        
            self.connection.putheader('content-length', str(len(body_txt)))
            self.connection.endheaders()
        
            offs = 0
            for i in range(0, len(body_txt), BLOCKSIZE):
                offs += BLOCKSIZE
                self.connection.send(body_txt[i:offs])
        
        
            statusCode, statusMsg, headers = self.connection.getreply()
            response = self.connection.file.read()
                
            return self.parse_xml('MediaUrl',response)
        
        except Exception, e:
            print e
            return None
            
            
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

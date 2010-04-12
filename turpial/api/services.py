# -*- coding: utf-8 -*-

"""Módulo para manejar los servicios HTTP de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 05, 2009

import os
import time
import Queue
import urllib2
import logging
import threading
import traceback

from turpial.api.twitpic import TwitPicAPI
from turpial.api.s60tweetphoto import TweetPhotoAPI
from turpial.api.twitter_globals import TWEETPHOTO_KEY

def _py26_or_greater():
    import sys
    return sys.hexversion > 0x20600f0
    
if _py26_or_greater():
    import json
else:
    import simplejson as json
    
class ShortenObject:
    def __init__(self, query, json=False, url_quote=True, response_key=None):
        self.query = query
        self.json = json
        self.response_key = response_key
        self.url_quote = url_quote

URL_SERVICES = {
    "cli.gs": ShortenObject("http://cli.gs/api/v1/cligs/create?appid=gwibber&url=%s"),
    "is.gd": ShortenObject("http://is.gd/api.php?longurl=%s"),
    "tinyurl.com": ShortenObject("http://tinyurl.com/api-create.php?url=%s"),
    "tr.im": ShortenObject("http://tr.im/api/trim_simple?url=%s"),
    "bit.ly": ShortenObject("http://api.bit.ly/shorten?version=2.0.1&login=turpial&apiKey=R_5a84eae6dd4158a0636358c4f9efdecc&longUrl=%s",
        True, True, 'shortUrl'),
    "smlk.es": ShortenObject("http://smlk.es/api/create/?destination=%s",
        True, True, 'link'),
    "su.pr": ShortenObject("http://su.pr/api/simpleshorten?url=%s"),
    "u.nu": ShortenObject("http://u.nu/unu-api-simple?url=%s"),
    #"sku.nu": ShortenObject("http://sku.nu?url=%s"),
}

PHOTO_SERVICES = [
    "TweetPhoto",
    "TwitPic",
]


class HTTPServices(threading.Thread):
    def __init__(self, username='', password='', imgdir='/tmp'):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.log = logging.getLogger('Services')
        self.queue = Queue.Queue()
        self.exit = False
        self.imgdir = imgdir
        self.username = username
        self.password = password
        self.log.debug('Iniciado')
        
    def set_credentials(self, username, password):
        '''Definicion de credenciales'''
        self.username = username
        self.password = password
        
    def update_img_dir(self, imgdir):
        self.imgdir = imgdir
        
    def download_pic(self, user, pic_url, callback):
        self.register({'cmd': 'download_pic', 'user': user, 'url': pic_url},
                      callback)
    
    def short_url(self, service, url, callback):
        self.register({'cmd': 'short_url', 'service': service, 'url': url},
                      callback)
    
    def upload_pic(self, service, path, callback):
        self.register({'cmd': 'upload_pic', 'service': service, 'path': path},
                      callback)
        
    def register(self, args, callback):
        self.queue.put((args, callback))
        
    def quit(self):
        self.exit = True
        
    def run(self):
        while not self.exit:
            time.sleep(0.3)
            try:
                req = self.queue.get(False)
            except Queue.Empty:
                continue
            
            (args, callback) = req
            if args['cmd'] == 'download_pic':
                ext = args['url'][-3:]
                if ext == '':
                    ext = 'png'
                filename = args['url'].replace('http://', '0_')
                filename = filename.replace('/', '_')
                fullname = os.path.join(self.imgdir, filename)
                
                try:
                    f = urllib2.urlopen(args['url']).read()
                except:
                    self.register(args, callback)
                    continue
                    
                _file = open(fullname, 'w+')
                _file.write(f)
                _file.close()
                
                self.log.debug('Descargada imagen de usuario: %s' % 
                               args['user'])
                callback(args['user'], filename)
                
            elif args['cmd'] == 'short_url':
                self.log.debug('Cortando URL: %s' % args['url'])
                
                key_url = args['url']
                service = URL_SERVICES[args['service']]
                if service.url_quote:
                    longurl = urllib2.quote(args['url'])
                    longurl = longurl.replace('/', '%2F')
                else:
                    longurl = args['url']
                
                try:
                    req = service.query % longurl
                    self.log.debug('Request: %s' % req)
                    if service.json:
                        resp = json.loads(urllib2.urlopen(req).read())
                        print resp
                        if args['service'] == "bit.ly":
                            short = resp['results'][key_url][service.response_key]
                        elif args['service'] == "siguemilink":
                            short = "http://www.siguemilink.com/%s" % \
                                resp[service.response_key]
                    else:
                        short = urllib2.urlopen(req).read()
                except Exception, error:
                    self.log.debug("Error: %s\n%s" % (error,
                                                      traceback.print_exc()))
                    short = None
                self.log.debug('URL Cortada: %s' % short)
                callback(short)
            elif args['cmd'] == 'upload_pic':
                self.log.debug('Subiendo imagen [%s]: %s' % 
                               (args['service'], args['path']))
                if args['service'] == "TweetPhoto":
                    api = TweetPhotoAPI(self.username, self.password,
                                        TWEETPHOTO_KEY)
                    rtn = api.upload(image=args['path'])
                    callback(rtn)
                elif args['service'] == "TwitPic":
                    api = TwitPicAPI(self.username, self.password)
                    rtn = api.upload(image=args['path'])
                    callback(rtn)
                else:
                    callback(None)
                
        
        self.log.debug('Terminado')
        return
        

# -*- coding: utf-8 -*-

# Módulo para manejar los servicios HTTP de Turpial
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

from s60tweetphoto import *
from twitpic import *
from twitter_globals import *

def _py26OrGreater():
    import sys
    return sys.hexversion > 0x20600f0
    
if _py26OrGreater():
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
        True, False, 'shortUrl'),
    "su.pr": ShortenObject("http://su.pr/api/simpleshorten?url=%s"),
    "u.nu": ShortenObject("http://u.nu/unu-api-simple?url=%s"),
    #"sku.nu": ShortenObject("http://sku.nu?url=%s"),
}

PHOTO_SERVICES = [
    "TweetPhoto",
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
        self.username = username
        self.password = password
        
    def update_img_dir(self, imgdir):
        self.imgdir = imgdir
        
    def download_pic(self, user, pic_url, callback):
        self.register({'cmd': 'download_pic', 'user': user, 'url': pic_url}, callback)
    
    def short_url(self, service, url, callback):
        self.register({'cmd': 'short_url', 'service': service, 'url': url}, callback)
    
    def upload_pic(self, service, path, callback):
        self.register({'cmd': 'upload_pic', 'service': service,  'path': path}, callback)
        
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
                if ext == '': ext = 'png'
                filename = args['url'].replace('http://', '0_')
                filename = filename.replace('/', '_')
                fullname = os.path.join(self.imgdir, filename)
                
                try:
                    f = urllib2.urlopen(args['url']).read()
                except:
                    self.register(args, callback)
                    continue
                    
                file = open(fullname, 'w+')
                file.write(f)
                file.close()
                
                self.log.debug('Descargada imagen de usuario: %s' % args['user'])
                callback(args['user'], filename)
                
            elif args['cmd'] == 'short_url':
                self.log.debug('Cortando URL: %s' % args['url'])
                
                service = URL_SERVICES[args['service']]
                if service.url_quote:
                    longurl = urllib2.quote(args['url'])
                else:
                    longurl = args['url']
                
                try:
                    req = service.query % longurl
                    self.log.debug('Request: %s' % req)
                    if service.json:
                        resp = json.loads(urllib2.urlopen(req).read())
                        short = resp['results'][longurl][service.response_key]
                    else:
                        short = urllib2.urlopen(req).read()
                except Exception, e:
                    self.log.debug("Error: %s\n%s" % (e, traceback.print_exc()))
                    short = None
                self.log.debug('URL Cortada: %s' % short)
                callback(short)
            elif args['cmd'] == 'upload_pic':
                self.log.debug('Subiendo imagen [%s]: %s' % (args['service'], args['path']))
                if args['service'] == "TweetPhoto":
                    api = TweetPhotoAPI(self.username, self.password, TWEETPHOTO_KEY)
                    rtn = api.upload(image=args['path'])
                    callback(rtn)
                elif args['service'] == "TwitPic":
                    api = TwitPicAPI(self.username, self.password)
                    rtn = api.upload(image=args['path'])
                    callback(rtn)
                else:
                    callback(rtn)
                
        
        self.log.debug('Terminado')
        return
        

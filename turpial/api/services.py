# -*- coding: utf-8 -*-

"""Módulo para manejar los servicios HTTP de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 05, 2009

import time
import Queue
import logging
import traceback
import threading

from turpial.api.twitpic import TwitPicAPI
from turpial.api.s60tweetphoto import TweetPhotoAPI
from turpial.api.twitter_globals import TWEETPHOTO_KEY
from turpial.api.interfaces.generic import GenericService
from turpial.api.interfaces.shorturl.cligs import CligsURLShorter
from turpial.api.interfaces.shorturl.isgd import IsgdURLShorter
from turpial.api.interfaces.shorturl.tinyurl import TinyurlURLShorter
from turpial.api.interfaces.shorturl.trim import TrimURLShorter
from turpial.api.interfaces.shorturl.bitly import BitlyURLShorter
from turpial.api.interfaces.shorturl.smlkes import SmlkesURLShorter
from turpial.api.interfaces.shorturl.supr import SuprURLShorter
from turpial.api.interfaces.shorturl.unu import UnuURLShorter

URL_SERVICES = {
    "cli.gs": CligsURLShorter(),
    "is.gd": IsgdURLShorter(),
    "tinyurl.com": TinyurlURLShorter(),
    "tr.im": TrimURLShorter(),
    "bit.ly": BitlyURLShorter(),
    "smlk.es": SmlkesURLShorter(),
    "su.pr": SuprURLShorter(),
    "u.nu": UnuURLShorter(),
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
                try:
                    filename = GenericService._download_pic(self.imgdir, 
                        args['url'])
                    self.log.debug('Descargada imagen de %s' % args['user'])
                    callback(args['user'], filename)
                except Exception, error:
                    self.log.debug("Error: %s\n%s" % (error, 
                        traceback.print_exc()))
                    self.register(args, callback)
            elif args['cmd'] == 'short_url':
                self.log.debug('Cortando URL: %s' % args['url'])
                urlshorter = URL_SERVICES[args['service']]
                resp = urlshorter.do_service(args['url'])
                self.log.debug('URL Cortada: %s' % resp.response)
                callback(resp)
                
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
        

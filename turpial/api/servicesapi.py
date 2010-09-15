# -*- coding: utf-8 -*-

"""Módulo para manejar los servicios HTTP de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 05, 2009

import Queue
import logging
import traceback
import threading

from turpial.api.interfaces.service import GenericService
from turpial.api.services.shorturl.cligs import CligsURLShorter
from turpial.api.services.shorturl.isgd import IsgdURLShorter
from turpial.api.services.shorturl.tinyurl import TinyurlURLShorter
from turpial.api.services.shorturl.trim import TrimURLShorter
from turpial.api.services.shorturl.bitly import BitlyURLShorter
from turpial.api.services.shorturl.smlkes import SmlkesURLShorter
from turpial.api.services.shorturl.supr import SuprURLShorter
from turpial.api.services.shorturl.unu import UnuURLShorter
from turpial.api.services.shorturl.zima import ZimaURLShorter
from turpial.api.services.shorturl.ur1ca import Ur1caURLShorter

from turpial.api.services.uploadpic.imgly import ImglyPicUploader
from turpial.api.services.uploadpic.tweetphoto import TweetPhotoPicUploader
from turpial.api.services.uploadpic.twitpic import TwitpicPicUploader
from turpial.api.services.uploadpic.twitgoo import TwitgooPicUploader
from turpial.api.services.uploadpic.mobypicture import MobypicturePicUploader
from turpial.api.services.uploadpic.yfrog import YfrogPicUploader

URL_SERVICES = {
    "cli.gs": CligsURLShorter(),
    "is.gd": IsgdURLShorter(),
    "tinyurl.com": TinyurlURLShorter(),
    "tr.im": TrimURLShorter(),
    "bit.ly": BitlyURLShorter(),
    "smlk.es": SmlkesURLShorter(),
    "su.pr": SuprURLShorter(),
    "u.nu": UnuURLShorter(),
    "zi.ma": ZimaURLShorter(),
    "ur1.ca": Ur1caURLShorter(),
    #"sku.nu": ShortenObject("http://sku.nu?url=%s"),
}

PHOTO_SERVICES = {
    "TweetPhoto": TweetPhotoPicUploader(),
    "TwitPic": TwitpicPicUploader(),
    "img.ly": ImglyPicUploader(),
    "Twitgoo": TwitgooPicUploader(),
    "Yfrog": YfrogPicUploader(),
}

#"MobyPicture": MobypicturePicUploader(),

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
        '''Definiendo la salida'''
        self.log.debug('Saliendo')
        self.exit = True
        
    def run(self):
        while not self.exit:
            try:
                req = self.queue.get(True, 0.3)
            except Queue.Empty:
                continue
            except:
                continue
            
            (args, callback) = req
            
            if self.exit:
                self.queue.task_done()
                break
                
            if args['cmd'] == 'download_pic':
                try:
                    filename = GenericService._download_pic(self.imgdir, args['url'])
                    self.log.debug('Descargada imagen de %s' % args['user'])
                    callback(args['user'], filename)
                except Exception, error:
                    rtn = error.read()
                    print 'Message:', rtn
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
                uploader = PHOTO_SERVICES[args['service']]
                resp = uploader.do_service(self.username, self.password, 
                    args['path'])
                callback(resp)
                
            self.queue.task_done()
            
        self.log.debug('Terminado')
        return
        

# -*- coding: utf-8 -*-

# Módulo para manejar los servicios HTTP de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 05, 2009

import os
import Queue
import urllib2
import logging
import threading

URL_SERVICES = {
    "cli.gs": "http://cli.gs/api/v1/cligs/create?appid=gwibber&url=%s",
    "is.gd": "http://is.gd/api.php?longurl=%s",
    "tinyurl.com": "http://tinyurl.com/api-create.php?url=%s",
    "tr.im": "http://tr.im/api/trim_simple?url=%s",
    #"bit.ly": "http://api.bit.ly/shorten?version=2.0.1&longUrl=%s&login=turpial&apiKey=R_5a84eae6dd4158a0636358c4f9efdecc",
    #"su.pr": "http://su.pr/api/shorten?longUrl=%s",
    "u.nu": "http://u.nu/unu-api-simple?url=%s"
}

class HTTPServices(threading.Thread):
    def __init__(self, imgdir='/tmp'):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.log = logging.getLogger('Services')
        self.queue = Queue.Queue()
        self.exit = False
        self.imgdir = imgdir
        self.log.debug('Iniciado')
        
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
                longurl = urllib2.quote(args['url'])
                try:
                    short = urllib2.urlopen(URL_SERVICES[args['service']] % longurl).read()
                except:
                    short = None
                self.log.debug('URL Cortada: %s' % short)
                callback(short)
        
        self.log.debug('Terminado')
        return
        
class URLShorten:
    
    def short(self, service, url):
        longurl = urllib2.quote(url)
        short = urllib2.urlopen(URL_SERVICES[service] % longurl).read()
        return short

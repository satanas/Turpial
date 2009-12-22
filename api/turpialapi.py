# -*- coding: utf-8 -*-

# Modelo base basado en hilos para el Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 22, 2009

import Queue
import logging
import threading

class TurpialAPI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.log = logging.getLogger('API')
        self.queue = Queue.Queue()
        self.exit = False
        
        self.twitter = None
        self.twitterapi = None
        self.search = Twitter(domain="search.twitter.com")
        self.agent = 'Turpial'
        
        self.log.debug('Iniciado')
        
    def auth(self, username, password):
        self.twitter = Twitter(email=username, password=password, agent=self.agent)
        self.twitterapi = Twitter(email=username, password=password, agent=self.agent, domain="api.twitter.com", uri="1")
        
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
                fullname = os.path.join('/tmp', filename)
                
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
                short = urllib2.urlopen(SERVICES[args['service']] % longurl).read()
                self.log.debug('URL Cortada: %s' % short)
                callback(short)
        
        self.log.debug('Terminado')
        return

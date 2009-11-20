# -*- coding: utf-8 -*-

# Modulo para descargar las imagenes de los usuarios en segundo plano
#
# Author: Wil Alvarez (aka Satanas)
# Nov 19, 2009

import os
import gtk
import urllib
import threading

SIZE = 48

class PicDownloader(threading.Thread):
    def __init__(self, url, user, callback):
        threading.Thread.__init__(self)
        self.url = url
        self.user = user
        self.callback = callback
        
    def run(self):
        ext = self.url[-3:]
        filename = self.url[self.url.rfind('/') + 1:]
        fullname = os.path.join('pixmaps', filename)

        urllib.urlretrieve(self.url, fullname)
        pix = gtk.gdk.pixbuf_new_from_file(fullname)
        pw = pix.get_width()
        ph = pix.get_height()
        
        if pw >= ph:
            ratio = float(ph)/pw
            fw = SIZE
            fh = int(fw * ratio)
        else:
            ratio = float(pw)/ph
            fh = SIZE
            fw = int(fh * ratio)
        
        img = pix.scale_simple(fw, fh, gtk.gdk.INTERP_BILINEAR)
        type = ext
        if ext == 'jpg': type = 'jpeg'
        if img: img.save(fullname, type)
        
        self.callback(self.user, filename)

#def hola(user, filename):
#    print 'listo'
#    
#p = PicDownloader('http://a1.twimg.com/profile_images/503858542/yo2_normal.png', 'prueba', hola)
#p.start()

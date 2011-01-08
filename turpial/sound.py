# -*- coding: utf-8 -*-

"""Clase para reproducir sonidos en múltiples plataformas en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Ene 08, 2010

import os
import logging
import traceback

from pygame import mixer as pygamemixer
from pygame import error as pygameerror

class Sound:
    def __init__(self, disable):
        self.sound = False
        self.log = logging.getLogger('Sound')
        self.disable = disable
        if self.disable:
            self.log.debug('Módulo deshabilitado')
            return
        
        try:
            pygamemixer.init()
            self.log.debug('Iniciado')
            self.sound = True
        except Exception, exc:
            self.log.debug(traceback.print_exc())
            self.sound = False
        
    def __play(self, filename):
        if self.disable:
            self.log.debug('Módulo deshabilitado. No hay sonidos')
            return
        path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            'data', 'sounds', filename))
        
        if not self.sound: 
            return
            
        try:
            sound = pygamemixer.Sound(path)
            sound.set_volume(0.6)
            sound.play()
        except pygameerror, message:
            self.log.debug('Can\'t load sound: %s\nDetails: %s' % (path, 
                message))
        
    def login(self):
        self.__play('cambur_pinton.ogg')
        
    def tweets(self):
        self.__play('turpial.ogg')
        
    def replies(self):
        self.__play('mencion3.ogg')
        
    def directs(self):
        self.__play('mencion2.ogg')

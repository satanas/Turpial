# -*- coding: utf-8 -*-

"""Clase para reproducir sonidos en múltiples plataformas en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Ene 08, 2010

import os
from pygame import mixer as pygamemixer
from pygame import error as pygameerror

class Sound:
    def __init__(self):
        pygamemixer.init()
        
    def __play(self, filename):
        path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            'data', 'sounds', filename))
        if not pygamemixer: 
            return
            
        try:
            sound = pygamemixer.Sound(path)
            sound.set_volume(0.6)
            sound.play()
        except pygameerror, message:
            print 'Cannot load sound:', path
            print message
        
    def login(self):
        self.__play('cambur_pinton.ogg')
        
    def tweets(self):
        self.__play('turpial.ogg')
        
    def replies(self):
        self.__play('mencion3.ogg')
        
    def directs(self):
        self.__play('mencion2.ogg')

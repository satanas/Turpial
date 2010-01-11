# -*- coding: utf-8 -*-

# Clase para reproducir sonidos en múltiples plataformas en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Ene 08, 2010

import os

if os.name == 'nt':
    import winsound

class Sound:
    def __play(self, file):
        path = os.path.join('sounds', file)
        if os.name == "nt":
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif os.name == "posix":
            if os.path.isfile('/usr/bin/aplay'):
                os.popen4("aplay " + path)
            elif os.path.isfile('/usr/bin/play'):
                os.popen4("play " + path)
            
    def login(self):
        self.__play('cambur_pinton.wav')
        
    def tweets(self):
        self.__play('turpial.wav')
        
    def replies(self):
        self.__play('mencion3.wav')
        
    def directs(self):
        self.__play('mencion2.wav')

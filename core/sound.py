# -*- coding: utf-8 -*-

# Clase para reproducir sonidos en múltiples plataformas en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Ene 08, 2010

import os

GST = False

if os.name == 'nt':
    import winsound
elif os.name == "posix":
    try:
        import gst
        GST = True
    except ImportError:
        pass
elif os.name == 'mac':
    from AppKit import NSSound

class Sound:
    
    def __play(self, file):
        path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', 'data', 'sounds', file))
        print path
        if os.name == "nt":
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif os.name == "posix":
            if GST:
                _player = gst.element_factory_make("playbin", "player")
                uri = "file://" + os.path.abspath(path)
                _player.set_property('uri', uri)
                _player.set_state(gst.STATE_PLAYING)
            else:
                if os.path.isfile('/usr/bin/aplay'):
                    play = lambda path: os.popen4('play ' + path)
                elif os.path.isfile('/usr/bin/play'):
                    play = lambda path: os.popen4('aplay ' + path)
                else:
                    play = dummy_play
        elif os.name == 'mac':
            macsound = NSSound.alloc()
            macsound.initWithContentsOfFile_byReference_(path, True)
            macsound.play()
        else:
            play = dummy_play
    
    def dummy_play(self, path):
        """
        dummy method used when no method is available
        """
        pass
    
    def login(self):
        self.__play('cambur_pinton.wav')
        
    def tweets(self):
        self.__play('turpial.wav')
        
    def replies(self):
        self.__play('mencion3.wav')
        
    def directs(self):
        self.__play('mencion2.wav')

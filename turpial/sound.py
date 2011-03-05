# -*- coding: utf-8 -*-

"""Clase para reproducir sonidos en múltiples plataformas en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Ene 08, 2010

import os
import ao
import logging
import platform
import traceback
import ogg.vorbis

class Sound:
    def __init__(self, disable):
        self.sound = False
        self.log = logging.getLogger('Sound')
        self.disable = disable
        if self.disable:
            self.log.debug('Módulo deshabilitado')
            return
            
        try:
            driver = self.__get_driver()
            self.device = ao.AudioDevice(ao.driver_id(driver), channels=1)
            self.log.debug('Iniciado con driver %s' % driver.upper())
            self.sound = True
        except Exception, exc:
            self.log.debug(traceback.print_exc())
            self.sound = False
    
    def __test_driver(self, driver):
        try:
            dummy = ao.AudioDevice(ao.driver_id(driver), channels=1)
            return True
        except:
            return False
            
    def __get_driver(self):
        #return 'macosx' for macos systems
        if platform.system() == 'Windows':
            return 'wmm'
        elif platform.system() == 'Linux':
            if self.__test_driver('alsa'):
                return 'alsa'
            elif self.__test_driver('pulse'):
                return 'pulse'
            elif self.__test_driver('oss'):
                return 'oss'
            elif self.__test_driver('esd'):
                return 'esd'
            elif self.__test_driver('arts'):
                return 'arts'
            else:
                return 'null'
                
    def play(self, filename):
        if self.disable:
            self.log.debug('Módulo deshabilitado. No hay sonidos')
            return
        path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            'data', 'sounds', filename))
        
        if not self.sound: 
            return
        
        vf = ogg.vorbis.VorbisFile(path)
        while 1:
            buff, bytes, _ = vf.read(4096)
            if bytes != 0:
                self.device.play(buff, bytes)
            else:
                vf.time_seek(0)
                return
        
    def login(self):
        self.play('cambur_pinton.ogg')
        
    def tweets(self):
        self.play('turpial.ogg')
        
    def replies(self):
        self.play('mencion3.ogg')
        
    def directs(self):
        self.play('mencion2.ogg')

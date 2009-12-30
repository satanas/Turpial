# -*- coding: utf-8 -*-

# Módulo para manejar los archivos de configuración de usuario del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 24, 2009

import os
import base64
import logging
import ConfigParser

class ConfigHandler:
    def __init__(self, user):
        self.__config = {}
        self.cfg = ConfigParser.ConfigParser()
        self.dir = os.path.join(os.path.expanduser('~'),'.config', 'turpial', user)
        self.filepath = os.path.join(self.dir, 'config')
        self.log = logging.getLogger('Config')
        
        # Create config file
        if not os.path.isfile(self.filepath):
            try:
                os.makedirs(self.dir)
            except:
                pass
            
            fd = open(self.filepath,'w')
            self.cfg.read(self.filepath)
            
            # Write user config
            self.cfg.add_section('Auth')
            self.cfg.set('Auth','oauth-key', '')
            self.cfg.set('Auth','oauth-secret', '')
            self.cfg.set('Auth','oauth-verifier', '')
            
            # Write general config
            self.cfg.add_section('General')
            self.cfg.set('General','home-update-interval', 3)
            self.cfg.set('General','replies-update-interval', 10)
            self.cfg.set('General','directs-update-interval', 15)
            self.cfg.set('General','workspace', 'single')
            self.cfg.set('General','profile-color', False)
            self.cfg.set('General','remember-login-info', False)
            self.cfg.set('General','minimize-on-close', False)
            self.cfg.set('General','main-win-geometry','320,480')
            
            self.cfg.write(fd)
            fd.close()
        
        self.load()

    def load(self):
        self.cfg.read(self.filepath)
        
        self.__config = {
            'Auth':{
                'oauth-key': self.cfg.get('Auth','oauth-key'),
                'oauth-secret': self.cfg.get('Auth','oauth-secret'),
                'oauth-verifier': self.cfg.get('Auth','oauth-verifier'),
            },
            'General':{
                'home-update-interval': self.cfg.get('General','home-update-interval'),
                'replies-update-interval': self.cfg.get('General','replies-update-interval'),
                'directs-update-interval': self.cfg.get('General','directs-update-interval'),
                'workspace': self.cfg.get('General','workspace'),
                'profile-color': self.cfg.get('General','profile-color'),
                'remember-login-info': self.cfg.get('General','remember-login-info'),
                'minimize-on-close': self.cfg.get('General','minimize-on-close'),
                'main-win-geometry': self.cfg.get('General','main-win-geometry'),
            },
        }
    
    def save(self, config):
        for section in config:
            for option in config[section]:
                value = config[section][option]
                self.write(section, option, value)
        
    def write(self, section, option, value):
        fd = open(self.filepath,'w')
        self.cfg.set(section, option, value)
        self.cfg.write(fd)
        fd.close()
        self.__config[section][option] = value
        
    def read(self, section, option):
        try:
            return self.__config[section][option]
        except:
            return None
            
    def read_section(self, section):
        try:
            return self.__config[section]
        except:
            return None

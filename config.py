# -*- coding: utf-8 -*-

# Módulo para manejar los archivos de configuración de usuario del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 24, 2009

import os
import logging
import ConfigParser

class ConfigHandler:
    def __init__(self, user):
        self.__config = {}
        self.cfg = ConfigParser.ConfigParser()
        self.dir = os.path.join(os.path.expanduser('~'),'.config', 'turpial', user)
        self.imgdir = os.path.join(self.dir, 'images')
        self.filepath = os.path.join(self.dir, 'config')
        self.log = logging.getLogger('Config')
        
        if not os.path.isdir(self.dir): os.makedirs(self.dir)
        if not os.path.isdir(self.imgdir): os.makedirs(self.imgdir)
        
        #if os.path.isfile(self.filepath):
            
        # Create config file
        if not os.path.isfile(self.filepath):
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
            self.cfg.set('General','profile-color', 'on')
            self.cfg.set('General','remember-login-info', 'off')
            self.cfg.set('General','minimize-on-close', 'on')
            self.cfg.set('General','main-win-geometry','320,480')
            
            # Write general config
            self.cfg.add_section('Notifications')
            self.cfg.set('Notifications','login', 'on')
            self.cfg.set('Notifications','home', 'on')
            self.cfg.set('Notifications','replies', 'on')
            self.cfg.set('Notifications','directs', 'on')
            
            # Write general config
            self.cfg.add_section('Services')
            self.cfg.set('Services','shorten-url', 'is.gd')
            self.cfg.set('Services','upload-pic', '')
            
            # Write general config
            self.cfg.add_section('Muted')
            self.cfg.set('Muted','users', '')
            
            self.cfg.write(fd)
            fd.close()
        
        self.load()

    def load(self):
        self.log.debug('Cargando')
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
            'Notifications':{
                'login': self.cfg.get('Notifications','login'),
                'home': self.cfg.get('Notifications','home'),
                'replies': self.cfg.get('Notifications','replies'),
                'directs': self.cfg.get('Notifications','directs'),
            },
            'Services':{
                'shorten-url': self.cfg.get('Services','shorten-url'),
                'upload-pic': self.cfg.get('Services','upload-pic'),
            },
            'Muted':{
                'users': self.cfg.get('Muted','users'),
            },
        }
    
    def save(self, config):
        self.log.debug('Guardando todo')
        for section, v in config.iteritems():
            for option, value in config[section].iteritems():
                if self.__config[section][option] != value:
                    self.write(section, option, value)
        
    def write(self, section, option, value):
        #self.log.debug('Guardando valor %s, %s, %s' % (section, option, value))
        fd = open(self.filepath,'w')
        self.cfg.set(section, option, value)
        self.cfg.write(fd)
        fd.close()
        self.__config[section][option] = value
        
    def read(self, section, option):
        #self.log.debug(u'Leyendo valor %s, %s' % (section, option))
        try:
            return self.__config[section][option]
        except:
            return None
            
    def read_section(self, section):
        self.log.debug(u'Leyendo sección %s' % (section))
        try:
            return self.__config[section]
        except:
            return None
            
    def read_all(self):
        self.log.debug('Leyendo todo')
        try:
            return self.__config
        except:
            return None

# -*- coding: utf-8 -*-

# Módulo para manejar los archivos de configuración de usuario del Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 24, 2009

import os
import logging
import ConfigParser

GLOBAL_CFG = {
    'App':{
        'version': '1.0-b2',
    },
    'Login':{
        'username': '',
        'password': '',
    },
    'Proxy':{
        'username': '',
        'password': '',
        'server': '',
        'port': '',
    }
}
DEFAULT_CFG = {
    'Auth':{
        'oauth-key': '',
        'oauth-secret': '',
        'oauth-verifier': '',
    },
    'General':{
        'home-update-interval': '3',
        'replies-update-interval': '10',
        'directs-update-interval': '15',
        'workspace': 'single',
        'profile-color': 'on',
        'remember-login-info': 'off',
        'minimize-on-close': 'on',
        'single-win-size': '320,480',
        'wide-win-size': '960,480',
        'window-position': '-1,-1',
        'num-tweets': '60',
    },
    'Notifications':{
        'sound': 'on',
        'login': 'on',
        'home': 'on',
        'replies': 'on',
        'directs': 'on',
    },
    'Services':{
        'shorten-url': 'is.gd',
        'upload-pic': 'TweetPhoto',
    },
}

class ConfigBase:
    def __init__(self, default=DEFAULT_CFG):
        self.__config = {}
        self.default = default
        self.cfg = ConfigParser.ConfigParser()
        self.filepath = ''
        self.log = logging.getLogger('Config')
    
    def create(self):
        self.log.debug('Creando archivo')
        fd = open(self.filepath,'w')
        for section, v in self.default.iteritems():
            self.cfg.add_section(section)
            for option, value in self.default[section].iteritems():
                self.cfg.set(section, option, value)
        self.cfg.write(fd)
        fd.close()
        
    def load(self):
        self.log.debug('Cargando archivo')
        self.cfg.read(self.filepath)
        
        for section, _v in self.default.iteritems():
            if not self.__config.has_key(section): self.__config[section] = {}
            if not self.cfg.has_section(section): 
                self.write_section(section, self.default[section])
            for option, value in self.default[section].iteritems():
                if self.cfg.has_option(section, option):
                    self.__config[section][option] = self.cfg.get(section, option)
                else:
                    self.write(section, option, value)
                
    def save(self, config):
        self.log.debug('Guardando todo')
        fd = open(self.filepath,'w')
        for section, _v in config.iteritems():
            for option, value in config[section].iteritems():
                self.cfg.set(section, option, value)
                self.__config[section][option] = value
        self.cfg.write(fd)
        fd.close()
        
    def write(self, section, option, value):
        fd = open(self.filepath,'w')
        self.cfg.set(section, option, value)
        self.cfg.write(fd)
        fd.close()
        self.__config[section][option] = value
        
    def write_section(self, section, items):
        fd = open(self.filepath,'w')
        self.cfg.add_section(section)
        for option, value in items.iteritems():
            self.cfg.set(section, option, value)
            self.__config[section][option] = value
        
        self.cfg.write(fd)
        fd.close()
        
    def read(self, section, option):
        try:
            return self.__config[section][option]
        except Exception:
            return None
            
    def read_section(self, section):
        self.log.debug(u'Leyendo sección %s' % (section))
        try:
            return self.__config[section]
        except Exception:
            return None
            
    def read_all(self):
        self.log.debug('Leyendo todo')
        try:
            return self.__config
        except Exception:
            return None

class ConfigHandler(ConfigBase):
    def __init__(self, user):
        ConfigBase.__init__(self)
        
        self.dir = os.path.join(os.path.expanduser('~'), '.config', 'turpial', user)
        self.imgdir = os.path.join(self.dir, 'images')
        self.filepath = os.path.join(self.dir, 'config')
        self.mutedpath = os.path.join(self.dir, 'muted')
        
        if not os.path.isdir(self.dir): 
            os.makedirs(self.dir)
        if not os.path.isdir(self.imgdir): 
            os.makedirs(self.imgdir)
        if not os.path.isfile(self.filepath): 
            self.create()
        if not os.path.isfile(self.mutedpath): 
            self.create_muted_list()
        
        self.load()
        
        #if self.__config['App']['version'] != DEFAULT['App']['version']:
        #    self.write('App', 'version', DEFAULT['App']['version'])
    
    def create_muted_list(self):
        fd = open(self.mutedpath,'w')
        fd.close()
        
    def load_muted_list(self):
        muted = []
        fd = open(self.mutedpath,'r')
        for line in fd:
            if line == '\n': continue
            muted.append(line.strip('\n'))
        fd.close()
        return muted
        
    def save_muted_list(self, lst):
        fd = open(self.mutedpath,'w')
        for user in lst:
            fd.write(user+'\n')
        fd.close()

class ConfigApp(ConfigBase):
    def __init__(self):
        ConfigBase.__init__(self, default=GLOBAL_CFG)
        
        self.dir = os.path.join(os.path.expanduser('~'), '.config', 'turpial')
        self.filepath = os.path.join(self.dir, 'global')
        
        if not os.path.isdir(self.dir): 
            os.makedirs(self.dir)
        if not os.path.isfile(self.filepath): 
            self.create()
        
        self.load()
        
        if self.read('App', 'version') != self.default['App']['version']:
            self.write('App', 'version', self.default['App']['version'])

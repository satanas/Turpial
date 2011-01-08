# -*- coding: utf-8 -*-

"""Módulo para manejar los archivos de configuración de usuario del Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 24, 2009

import os
import logging
import ConfigParser

try:
    from xdg import BaseDirectory
    XDG_CACHE = True
except:
    XDG_CACHE = False

PROTOCOLS = ['twitter', 'identica']

# Tipos de actualizaciones (tweets/dents)
UPDATE_TYPE_DM = 'dm'
UPDATE_TYPE_STD = 'std'
UPDATE_TYPE_PROFILE = 'profile'

GLOBAL_CFG = {
    'App':{
        'version': '1.4.9-a92',
    },
    'Proxy':{
        'username': '',
        'password': '',
        'server': '',
        'port': '',
        'url': '',
    }
}
PROTOCOL_CFG = {
    'Login':{
        'username': '',
        'password': '',
    }
}
DEFAULT_CFG = {
    'General':{
        'home-update-interval': '3',
        'replies-update-interval': '10',
        'directs-update-interval': '15',
        'workspace': 'single',
        'profile-color': 'on',
        'remember-login-info': 'off',
        'minimize-on-close': 'on',
        'num-tweets': '60',
    },
    'Window': {
        'single-win-size': '320,480',
        'wide-win-size': '960,480',
        'window-single-position': '-1,-1',
        'window-wide-position': '-1,-1',
        'window-state': 'windowed',
        'window-visibility': 'show',
    },
    'Columns':{
        'column1': 'timeline',
        'column2': 'replies',
        'column3': 'directs',
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
        'upload-pic': 'TwitPic',
    },
    'Browser':{
        'cmd': ''
    },
}


class ConfigBase:
    """Configuracion base de la aplicacion"""
    def __init__(self, default=None):
        self.__config = {}
        if default is None:
            self.default = DEFAULT_CFG
        else:
            self.default = default
        self.cfg = ConfigParser.ConfigParser()
        self.filepath = ''
        self.log = logging.getLogger('Config')
    
    def create(self):
        """Creacion de fichero de configuracion"""
        self.log.debug('Creando archivo')
        _fd = open(self.filepath, 'w')
        for section, v in self.default.iteritems():
            self.cfg.add_section(section)
            for option, value in self.default[section].iteritems():
                self.cfg.set(section, option, value)
        self.cfg.write(_fd)
        _fd.close()
        
    def load(self):
        """Carga de fichero de configuracion"""
        self.log.debug('Cargando configuración')
        self.cfg.read(self.filepath)
        
        for section, _v in self.default.iteritems():
            if not self.__config.has_key(section):
                self.__config[section] = {}
            if not self.cfg.has_section(section): 
                self.write_section(section, self.default[section])
            for option, value in self.default[section].iteritems():
                if self.cfg.has_option(section, option):
                    self.__config[section][option] = self.cfg.get(section,
                                                                  option)
                else:
                    self.write(section, option, value)
                
    def load_failsafe(self):
        self.log.debug('Cargada configuración failsafe')
        self.__config = self.default
        
    def save(self, config):
        """Guardando configuracion en fichero"""
        self.log.debug('Guardando todo')
        _fd = open(self.filepath, 'w')
        for section, _v in config.iteritems():
            for option, value in config[section].iteritems():
                self.cfg.set(section, option, value)
                self.__config[section][option] = value
        self.cfg.write(_fd)
        _fd.close()
        
    def write(self, section, option, value):
        _fd = open(self.filepath, 'w')
        self.cfg.set(section, option, value)
        self.cfg.write(_fd)
        _fd.close()
        self.__config[section][option] = value
        
    def write_section(self, section, items):
        _fd = open(self.filepath, 'w')
        self.cfg.add_section(section)
        for option, value in items.iteritems():
            self.cfg.set(section, option, value)
            self.__config[section][option] = value
        
        self.cfg.write(_fd)
        _fd.close()
        
    def read(self, section, option):
        """Lectura de opcion de una seccion del fichero de configuracion"""
        try:
            return self.__config[section][option]
        except Exception:
            return None
            
    def read_section(self, section):
        """Lectura de seccion de fichero de configuracion"""
        self.log.debug(u'Leyendo sección %s' % (section))
        try:
            return self.__config[section]
        except Exception:
            return None
            
    def read_all(self):
        """Lectura del fichero de configuracion"""
        self.log.debug('Leyendo todo')
        try:
            return self.__config
        except Exception:
            return None


class ConfigHandler(ConfigBase):
    """Manejador de la configuracion, creacion de estructura inicial de
    directorios, archivos y listas."""

    def __init__(self, user, protocol):
        ConfigBase.__init__(self)
        
        self.dir = os.path.join(os.path.expanduser('~'), '.config',
            'turpial', protocol, user)
        if XDG_CACHE:
            self.imgdir = os.path.join(BaseDirectory.xdg_cache_home, 
                'turpial', protocol, user, 'images')
        else:
            self.imgdir = os.path.join(self.dir, 'images')
        self.filepath = os.path.join(self.dir, 'config')
        self.mutedpath = os.path.join(self.dir, 'muted')
    
    def initialize_failsafe(self):
        if not os.path.isdir(self.dir): 
            self.load_failsafe()
        else:
            self.initialize()
            
    def initialize(self):
        self.log.debug('CACHEDIR: %s' % self.imgdir)
        self.log.debug('CONFIGFILE: %s' % self.filepath)
        self.log.debug('MUTEDFILE: %s' % self.mutedpath)
        
        if not os.path.isdir(self.dir): 
            os.makedirs(self.dir)
        if not os.path.isdir(self.imgdir): 
            os.makedirs(self.imgdir)
        if not os.path.isfile(self.filepath): 
            self.create()
        if not os.path.isfile(self.mutedpath): 
            self.create_muted_list()
        
        self.load()
        
    def create_muted_list(self):
        _fd = open(self.mutedpath, 'w')
        _fd.close()
        
    def load_muted_list(self):
        muted = []
        _fd = open(self.mutedpath, 'r')
        for line in _fd:
            if line == '\n':
                continue
            muted.append(line.strip('\n'))
        _fd.close()
        return muted
        
    def save_muted_list(self, lst):
        _fd = open(self.mutedpath, 'w')
        for user in lst:
            _fd.write(user + '\n')
        _fd.close()


class ConfigApp(ConfigBase):
    """Configuracion de la aplicacion"""
    
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
            
class ConfigProtocol(ConfigBase):
    """Configuracion del protocolo"""
    
    def __init__(self, protocol):
        ConfigBase.__init__(self, default=PROTOCOL_CFG)
        
        self.dir = os.path.join(os.path.expanduser('~'), '.config', 
            'turpial', protocol)
        self.filepath = os.path.join(self.dir, 'config')
        
        if not os.path.isdir(self.dir): 
            os.makedirs(self.dir)
        if not os.path.isfile(self.filepath): 
            self.create()
        
        self.load()

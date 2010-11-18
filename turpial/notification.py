# -*- coding: utf-8 -*-

"""Clase para manejar todas las notificaciones de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 27, 2009

import os
import logging

log = logging.getLogger('Notify')

try:
    import pynotify
    NOTIFY = True
except ImportError:
    log.debug("pynotify is not installed")
    NOTIFY = False

class Notification:
    """Manejo de notificaciones"""
    def __init__(self):
        self.activate()
        
    def toggle_activation(self):
        if self.active:
            self.active = False
        else:
            self.active = True

    def activate(self):
        self.active = True
        
    def deactivate(self):
        self.active = False
        
    def popup(self, title, message, icon=None):
        if self.active and NOTIFY:
            if pynotify.init("Turpial"):
                if not icon:
                    iconpath = os.path.join(os.path.dirname(__file__), 'data', 
                        'pixmaps', 'turpial-notification.png')
                    icon = os.path.realpath(iconpath)
                icon = "file://%s" % icon
                notification = pynotify.Notification(title, message, icon)
                notification.show()
    
    def new_tweets(self, title, count, tobject, tweet, icon):
        self.popup('%s (%i %s)' % (title, count, tobject), tweet, icon)
        
    def login(self, p):
        self.popup('@%s' % p.username,
            '%s: %i\n%s: %i\n%s: %i' % 
            (_('Tweets'), p.statuses_count,
            _('Following'), p.friends_count, 
            _('Followers'), p.followers_count))
    
    def following(self, user, follow):
        name = user.username
        if follow:
            self.popup(_('Turpial (Follow)'), _('You are now following @%s') % name)
        else:
            self.popup(_('Turpial (Unfollow)'), _('You are no longer following @%s') % name)
                
    def following_error(self, message, follow):
        if follow:
            self.popup(_('Turpial (Follow)'), message)
        else:
            self.popup(_('Turpial (Unfollow)'), message)

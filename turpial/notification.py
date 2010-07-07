# -*- coding: utf-8 -*-

"""Clase para manejar todas las notificaciones de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 27, 2009

import os
import logging

from turpial.sound import Sound

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
        self.play = True
        self.sound = Sound()
        
    def update_config(self, config):
        self.config = config
        
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
                
    def new_tweets(self, count, tweet, icon):
        if self.config['home'] != 'on':
            return
        if count == 1:
            twt = _('new tweet')
        else:
            twt = _('new tweets')
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
        if self.config['sound'] == 'on': 
            self.sound.tweets()
        
    def new_replies(self, count, tweet, icon):
        if self.config['replies'] != 'on':
            return
        if count == 1:
            twt = _('new mention')
        else:
            twt = _('new mentions')
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
        if self.config['sound'] == 'on':
            self.sound.replies()
            
    def new_directs(self, count, tweet, icon):
        if self.config['directs'] != 'on':
            return
        if count == 1: 
            twt = _('new DM') 
        else:
            twt = _('new DMs')
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
        if self.config['sound'] == 'on':
            self.sound.directs()
        
    def login(self, p):
        if self.config['login'] != 'on':
            return
        self.popup('@%s' % p.username,
            '%s: %i\n%s: %i\n%s: %i' % 
            (_('Tweets'), p.statuses_count,
            _('Following'), p.friends_count, 
            _('Followers'), p.followers_count))
        if self.config['sound'] == 'on':
            self.sound.login()
    
    def following(self, user, follow):
        name = user.username
        if follow:
            self.popup(_('Turpial (Follow)'), _('Now you follow to @%s') % name)
        else:
            self.popup(_('Turpial (Unfollow)'), _('You have unfollow to @%s') % name)
                
    def following_error(self, message, follow):
        if follow:
            self.popup(_('Turpial (Follow)'), message)
        else:
            self.popup(_('Turpial (Unfollow)'), message)

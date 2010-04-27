# -*- coding: utf-8 -*-

"""Clase para manejar todas las notificaciones de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 27, 2009

import os
import logging

from turpial.sound import Sound

log = logging.getLogger('Notify')

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
        try:
            import pynotify
            self.integrated = True
        except ImportError:
            log.debug("pynotify is not installed")
            self.integrated = False
        
        if self.active and self.integrated:
            if pynotify.init("Turpial"):
                if not icon:
                    icon = os.path.realpath(os.path.join(os.path.dirname(__file__),
                        'data', 'pixmaps', 'turpial_icon_48.png'))
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
        self.popup('@%s' % p['screen_name'],
            '%s: %i\n%s: %i\n%s: %i' % 
            (_('Tweets'), p['statuses_count'],
            _('Following'), p['friends_count'], 
            _('Followers'), p['followers_count']))
        if self.config['sound'] == 'on':
            self.sound.login()
        
    def following(self, user, follow):
        name = user['screen_name']
        
        if follow:
            self.popup(_('Follow'), _('Now you follow to @%s') % name)
        else:
            self.popup(_('Unfollow'), _('You have unfollow to @%s') % name)

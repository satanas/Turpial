# -*- coding: utf-8 -*-

# Clase para manejar todas las notificaciones de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 27, 2009

import logging

from core.sound import *

log = logging.getLogger('Notify')

class Notification:
    def __init__(self):
        self.activate()
        self.play = True
        self.sound = Sound()
        
    def update_config(self, config):
        self.config = config
        
    def activate(self):
        self.active = True
        
    def deactivate(self):
        self.active = False
        
    def popup(self, title, message, icon=None):
        try:
            import pynotify
            self.integrated = True
        except:
            log.debug("pynotify is not installed")
            self.integrated = False
        
        if self.active and self.integrated:
            if pynotify.init("Turpial"):
                if not icon:
                    icon = os.path.realpath(os.path.join(os.path.dirname(__file__),
                        '..', 'data', 'pixmaps', 'turpial_icon_48.png'))
                icon = "file://%s" % icon
                n = pynotify.Notification(title, message, icon)
                n.show()
                
    def new_tweets(self, count, tweet, icon):
        if self.config['home'] != 'on': return
        twt = 'nuevo tweet' if count == 1 else 'nuevos tweets'
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
        if self.config['sound'] == 'on': self.sound.tweets()
        
        
    def new_replies(self, count, tweet, icon):
        if self.config['replies'] != 'on': return
        twt = u'nueva mención' if count == 1 else u'nuevas menciones'
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
        if self.config['sound'] == 'on': self.sound.replies()
            
    def new_directs(self, count, tweet, icon):
        if self.config['directs'] != 'on': return
        twt = 'nuevo DM' if count == 1 else 'nuevos DM'
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
        if self.config['sound'] == 'on': self.sound.directs()
        
    def login(self, p):
        if self.config['login'] != 'on': return
        self.popup('@%s' % p['screen_name'], 
            'Tweets: %i\nFollowing: %i\nFollowers: %i' % (p['statuses_count'], 
            p['friends_count'], p['followers_count']))
        if self.config['sound'] == 'on': self.sound.login()
        
    def following(self, user, follow):
        name = user['screen_name']
        
        if follow:
            self.popup('Follow', 'Estas siguiendo a @%s' % name)
        else:
            self.popup('Unfollow', 'Has dejado de seguir a @%s' % name)

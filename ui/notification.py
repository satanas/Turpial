# -*- coding: utf-8 -*-

# Clase para manejar todas las notificaciones de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 27, 2009

import util
import logging

log = logging.getLogger('Notify')

class Notification:
    def __init__(self):
        self.activate()
        
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
        
        if self.active:
            if pynotify.init("Turpial"):
                if not icon:
                    icon = util.load_image('turpial_icon_48.png', True)
                #else:
                #    icon = util.load_avatar(icon, True)
                n = pynotify.Notification(title, message)
                n.set_icon_from_pixbuf(icon)
                n.show()
                
    def new_tweets(self, count, tweet, icon):
        twt = 'nuevo tweet' if count == 1 else 'nuevos tweets'
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
            
    def new_replies(self, count, tweet, icon):
        twt = u'nueva mención' if count == 1 else u'nuevas menciones'
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
            
    def new_directs(self, count, tweet, icon):
        twt = 'nuevo DM' if count == 1 else 'nuevos DM'
        self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
        
    def login(self, p):
        self.popup('@%s' % p['screen_name'], 
            'Tweets: %i\nFollowing: %i\nFollowers: %i' % (p['statuses_count'], 
            p['friends_count'], p['followers_count']))

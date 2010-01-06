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
                
    def new_tweets(self, count, updating, tweet, icon):
        if count > 0 and updating:
            twt = 'nuevo tweet' if count == 1 else 'nuevos tweets'
            #self.popup('Actualizado timeline', '%i tweets nuevos' % count, 'home.png')
            self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
            
    def new_replies(self, count, updating, tweet, icon):
        if count > 0 and updating:
            twt = u'nueva mención' if count == 1 else u'nuevas menciones'
            #self.popup('Actualizadas menciones', '%i menciones nuevas' % count, 'profile.png')
            self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)
            
    def new_directs(self, count, updating, tweet, icon):
        if count > 0 and updating:
            twt = 'nuevo DM' if count == 1 else 'nuevos DM'
            #self.popup('Actualizados mensajes directos', '%i mensajes nuevos' % count, 'lists.png')
            self.popup('Turpial (%i %s)' % (count, twt), tweet, icon)

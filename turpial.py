#!/usr/bin/python

# Controlador de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 8, 2009

import time
import logging
from api import *
from ui import *

logging.basicConfig(level=logging.DEBUG)

class Turpial:
    def __init__(self):
        self.twitter = None
        self.ui = cmdline.Main(self)
        self.agent = 'Turpial'
        
        self.log = logging.getLogger('Controller')
        self.log.debug('Iniciando Turpial')
        self.ui.show_login()
        self.ui.main_loop()
        
    def signup(self, username, password):
        #self.ui.show_main()
        #self.ui.cancel_login('bla')
        #return
        self.twitter = Twitter(email=username, password=password, agent=self.agent)
        try:
            self.twitter.account.verify_credentials()
            tweets = self.twitter.statuses.friends_timeline()
            #replies = self.twitter.statuses.mentions()
            #direct = self.twitter.direct_messages()
            #favs = self.twitter.favorites()
            rate = self.twitter.account.rate_limit_status()
            self.ui.show_main()
            self.ui.update_timeline(tweets)
            #self.ui.update_replies(replies)
            #self.ui.update_direct(direct)
            #self.ui.update_favorites(favs)
            self.ui.update_rate_limits(rate)
        except TwitterError, error:
            self.log.debug('Error verificando credenciales %s' % error)
            self.ui.cancel_login('Login info not valid')
        
        
if __name__ == '__main__':
    t = Turpial()

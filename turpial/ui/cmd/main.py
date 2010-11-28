# -*- coding: utf-8 -*-

# Vista para Turpial en PyGTK
#
# Author: Wil Alvarez (aka Satanas)
# Nov 08, 2009

import os
import base64
import logging

from turpial.ui.base_ui import BaseGui
from turpial.notification import Notification
from turpial.ui import util as util
from turpial.sound import Sound
from turpial.config import PROTOCOLS

log = logging.getLogger('console')


class Main(BaseGui):
    def __init__(self, controller,options,extend=False):
        BaseGui.__init__(self, controller)
        self.options=options
        self.controller=controller
    
    def quit(self, arg=None):
        self.request_signout()
        
    def main_loop(self):
        if not self.options.user:
            print "Debe ingresar el nombre de usuario"
            self.quit()
        if not self.options.passwd:
            print "Debe ingresar la contraseña de la cuenta"
            self.quit()
        if not self.options.message:
            print "Debe colocar un mensaje a postear"
            self.quit()
        self.controller.signin(self.options.user, self.options.passwd, PROTOCOLS[0])
        self.controller.update_status(self.options.message)
        
    def show_login(self):
        pass

    def tweet_done(self, tweets):
        log.debug(u'Actualizando nuevo tweet')
        self.quit()
        
    def resize_avatar(self, pic):
        pass
        
    def show_main(self, config, global_config,  profile):
        pass
        
    def set_lists(self, lists, viewed):
        pass
        
    def show_oauth_pin_request(self, url):
        pass
        
    def cancel_login(self):
        pass
        
    def start_updating_column1(self):
        pass
        
    def start_updating_column2(self):
        pass
        
    def start_updating_column3(self):
        pass
        
    def start_search(self):
        pass
        
    def update_tweet(self, tweet):
        pass
        
    def update_column1(self, tweets):
        pass
        
    def update_column2(self, replies):
        pass
        
    def update_column3(self, directs):
        pass
        
    def update_favorites(self, favs):
        pass
        
    def update_rate_limits(self, rates):
        pass
        
    def update_follow(self, user, follow):
        pass
        
    def update_user_avatar(self, user, avatar):
        pass
        
    def update_user_profile(self, profile):
        pass
        
    def update_search(self, topics):
        pass
        
    def update_in_reply_to(self, tweets):
        pass
        
    def update_conversation(self, tweets):
        pass
        
    def tweet_changed(self, timeline, replies, favs):
        pass
        
    def update_config(self, config):
        pass
    
    def set_column_item(self, index, reset=False):
        pass

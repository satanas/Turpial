# -*- coding: utf-8 -*-

# Clase Base para todas las interfaces gráficas de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 07, 2009

import os
import util
import Image
import logging

log = logging.getLogger('BaseUI')

class BaseGui:
    
    def __init__(self, controller):
        self.__controller = controller
        self.__user_pics = {}
        self.__queued_pics = []
        self.updating = {'home': False, 'replies': False, 'directs': False}
        
        
    # ------------------------------------------------------------
    # Private/Internal methods
    # ------------------------------------------------------------
    
    def __done_user_avatar(self, user, pic):
        log.debug('Actualizando imagen de usuario %s' % user)
        self.resize_avatar(pic)
        self.__user_pics[user] = pic
        self.__queued_pics.remove(pic)
        self.update_user_avatar(user, pic)
        
        
    # ------------------------------------------------------------
    # Common methods to all interfaces
    # ------------------------------------------------------------
    
    def resize_avatar(self, pic):
        ext = pic[-3:].lower()
        fullname = os.path.join('/tmp', pic)
        
        img = Image.open(fullname)
        pw, ph = img.size
        
        if pw >= ph:
            ratio = float(ph)/pw
            fw = util.AVATAR_SIZE
            fh = int(fw * ratio)
        else:
            ratio = float(pw)/ph
            fh = util.AVATAR_SIZE
            fw = int(fh * ratio)
        
        img2 = img.resize((fw, fh), Image.BICUBIC)
        img2.save(fullname)
        
    def request_signin(self, username, password):
        self.__controller.signin(username, password)
        
    def request_oauth(self, username, password):
        self.__controller.signin_oauth(username, password)
        
    def request_auth_token(self, pin):
        self.__controller.auth_token(pin)
        
    def request_signout(self):
        self.__controller.signout()
        
    def request_user_profile(self):
        return self.__controller.profile
        
    def request_user_avatar(self, user, pic_url):
        pic = pic_url.replace('http://', '0_')
        pic = pic.replace('/', '_')
        
        fullname = os.path.join('/tmp', pic)
        if os.path.isfile(fullname):
            self.__user_pics[user] = pic
            return self.__user_pics[user]
        if user in self.__user_pics: 
            return self.__user_pics[user]
        if pic in self.__queued_pics: 
            return None
        
        log.debug('Solicitando imagen de usuario %s' % user)
        self.__queued_pics.append(pic)
        self.__controller.download_user_pic(user, pic_url, self.__done_user_avatar)
        return None
        
    def request_retweet(self, id):
        self.__controller.retweet(id)
        
    def request_fav(self, id):
        self.__controller.set_favorite(id)
        
    def request_unfav(self, id):
        self.__controller.unset_favorite(id)
        
    def request_mute(self, user):
        self.__controller.mute(user)
        
    def request_unmute(self, user):
        self.__controller.unmute(user)
        
    def request_follow(self, user):
        self.__controller.follow(user)
        
    def request_unfollow(self, user):
        self.__controller.unfollow(user)
        
    def request_direct(self, user, message):
        log.debug('Enviando mensaje directo a %s' % user)
        # self.__controller.send_direct(user, message)
        
    def request_destroy_status(self, id):
        self.__controller.destroy_status(id)
        
    def request_short_url(self, longurl, callback):
        self.__controller.short_url(longurl, callback)
        
    def request_upload_pic(self, filename):
        self.__controller.upload_pic(filename)
        
    def request_update_status(self, text, in_reply_id):
        self.__controller.update_status(text, in_reply_id)
        
    def request_update_profile(self, new_name, new_url, new_bio, new_loc):
        self.__controller.update_profile(self, new_name, new_url, new_bio, new_loc)
        
    def request_search_topic(self, topic):
        self.__controller.search_topic(topic)
        
    def request_search_people(self, query):
        self.__controller.search_people(query)
        
    def request_trends(self):
        self.__controller._update_trends()
        
    def request_save_config(self, new_config):
        self.__controller.save_config(new_config)
        
    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------
    # Estos métodos deben ser llamados por la clase hija cada cierto tiempo
    
    def download_timeline(self):
        self.updating['home'] = True
        self.__controller._update_timeline()
        return True
        
    def download_replies(self):
        self.updating['replies'] = True
        self.__controller._update_replies()
        return True
        
    def download_directs(self):
        self.updating['directs'] = True
        self.__controller._update_directs()
        return True
        
    def download_rates(self):
        self.__controller._update_rate_limits()
        return True
        
    def download_favorites(self):
        self.__controller._update_favorites()
        
    def download_following(self):
        self.__controller._update_following()
        
    def download_followers(self):
        self.__controller._update_followers()
        
    # ------------------------------------------------------------
    # Methods to be overwritten
    # ------------------------------------------------------------
    
    def main_loop(self):
        raise NotImplementedError
        
    def show_login(self):
        raise NotImplementedError
        
    def show_main(self):
        raise NotImplementedError
        
    def show_oauth_pin_request(self, url):
        raise NotImplementedError
        
    def cancel_login(self):
        raise NotImplementedError
        
    def start_updating_timeline(self):
        raise NotImplementedError
        
    def start_updating_replies(self):
        raise NotImplementedError
        
    def start_updating_directs(self):
        raise NotImplementedError
        
    def update_tweet(self, tweet):
        raise NotImplementedError
        
    def update_timeline(self, tweets):
        raise NotImplementedError
        
    def update_replies(self, replies):
        raise NotImplementedError
        
    def update_directs(self, directs):
        raise NotImplementedError
        
    def update_favorites(self, favs):
        raise NotImplementedError
        
    def update_rate_limits(self, rates):
        raise NotImplementedError
        
    def update_following(self, followings):
        raise NotImplementedError
        
    def update_followers(self, followers):
        raise NotImplementedError
        
    def update_user_avatar(self, avatar):
        raise NotImplementedError
        
    def update_user_profile(self, profile):
        raise NotImplementedError
        
    def update_trends(self, current, day, week):
        raise NotImplementedError
        
    def update_search_topics(self, topics):
        raise NotImplementedError
        
    def tweet_changed(self, timeline, replies, favs):
        raise NotImplementedError
        
    def update_config(self, config):
        raise NotImplementedError
        

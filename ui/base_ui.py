# -*- coding: utf-8 -*-

# Clase Base para todas las interfaces gráficas de Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 07, 2009

import os
import util
#import Image
import logging
import xml.sax.saxutils as saxutils

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
        
    def __get_real_tweet(self, tweet):
        retweet_by = None
        if tweet.has_key('retweeted_status'):
            retweet_by = tweet['user']['screen_name']
            tweet = tweet['retweeted_status']
        
        return tweet, retweet_by
        
    # ------------------------------------------------------------
    # Common methods to all interfaces
    # ------------------------------------------------------------
    
    # :FIX: Quizas esto deba ir en 'util'
    def parse_tweet(self, xtweet):
        tweet, retweet_by = self.__get_real_tweet(xtweet)
        
        if tweet.has_key('user'):
            username = tweet['user']['screen_name']
            avatar = tweet['user']['profile_image_url']
        elif tweet.has_key('sender'):
            direct = True
            username = tweet['sender']['screen_name']
            avatar = tweet['sender']['profile_image_url']
        elif tweet.has_key('from_user'):
            username = tweet['from_user']
            avatar = tweet['profile_image_url']
        
        tweet['text'] = saxutils.unescape(tweet['text'])
        
        client = util.detect_client(tweet)
        datetime = util.get_timestamp(tweet)
        
        in_reply_to_id = None
        in_reply_to_user = None
        if tweet.has_key('in_reply_to_status_id') and tweet['in_reply_to_status_id']:
            in_reply_to_id = tweet['in_reply_to_status_id']
            in_reply_to_user = tweet['in_reply_to_screen_name']
        
        fav = False
        if tweet.has_key('favorited'): fav = tweet['favorited']
        
        return {'username': username, 'avatar': avatar, 'client': client, 
            'datetime':datetime, 'text': tweet['text'], 'id': tweet['id'],
            'in_reply_to_id': in_reply_to_id, 'in_reply_to_user': in_reply_to_user,
            'fav': fav, 'retweet_by': retweet_by}
        
    def after_destroy(self, timeline, favs):
        self.update_timeline(timeline)
        self.update_favorites(favs)
        
    def read_config(self):
        return self.__controller.config.read_all()
        
    def save_config(self, new_config, update=True):
        self.__controller.save_config(new_config, update)
        
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
        # pic = unicode(pic)
        fullname = os.path.join(self.imgdir, pic)
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
        
    def request_update_profile(self, name, url, bio, location):
        self.__controller.update_profile(name, url, bio, location)
        
    def request_search_topic(self, topic):
        self.__controller.search_topic(topic)
        
    def request_search_people(self, query):
        self.__controller.search_people(query)
        
    def request_trends(self):
        self.__controller._update_trends()
        
    def request_popup_info(self, tweet_id, user):
        return self.__controller.get_popup_info(tweet_id, user)
    
    def request_in_reply_to(self, tweet_id, user):
        self.__controller.in_reply_to(tweet_id)
        
    def request_conversation(self, tweet_id, user):
        self.__controller.get_conversation(tweet_id)
        
    def request_muted_list(self):
        return self.__controller.get_muted_list()
        
    def request_update_muted(self, muted_users):
        self.__controller.update_muted(muted_users)
        
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
        
    # ------------------------------------------------------------
    # Methods to be overwritten
    # ------------------------------------------------------------
    
    def resize_avatar(self, pic):
        raise NotImplemented
        
    def main_loop(self):
        raise NotImplementedError
        
    def show_login(self):
        raise NotImplementedError
        
    def show_main(self, config, profile):
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
        
    def start_search(self):
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
        
    def update_follow(self, user, follow):
        raise NotImplementedError
        
    def update_user_avatar(self, avatar):
        raise NotImplementedError
        
    def update_user_profile(self, profile):
        raise NotImplementedError
        
    def update_trends(self, current, day, week):
        raise NotImplementedError
        
    def update_search_topics(self, topics):
        raise NotImplementedError
    
    def update_friends(self, friends):
        raise NotImplementedError
        
    def update_in_reply_to(self, tweets):
        raise NotImplementedError
        
    def update_conversation(self, tweets):
        raise NotImplementedError
        
    def tweet_changed(self, timeline, replies, favs):
        raise NotImplementedError
        
    def tweet_done(self, tweets):
        raise NotImplementedError
        
    def update_config(self, config):
        raise NotImplementedError
        

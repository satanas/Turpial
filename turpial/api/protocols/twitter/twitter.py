# -*- coding: utf-8 -*-

"""Implementación del protocolo Twitter para Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 25, 2010

from turpial.api.interfaces.protocol import Protocol
from turpial.api.interfaces.http import TurpialException
from turpial.api.protocols.twitter.http import TwitterHTTP
from turpial.api.interfaces.post import Status, Response, Profile, List, RateLimit
from turpial.config import PROTOCOLS
from turpial.config import UPDATE_TYPE_DM, UPDATE_TYPE_STD, UPDATE_TYPE_PROFILE

class Twitter(Protocol):
    def __init__(self):
        Protocol.__init__(self, 'Twitter', 'http://api.twitter.com/1', 
            'http://search.twitter.com', 'http://twitter.com/search?q=%23',
            None, 'http://www.twitter.com')
        
        self.http = TwitterHTTP(self.apiurl)
        self.retweet_by_me = []
        self.oauth_support = False
        
    def __get_real_tweet(self, tweet):
        '''Get the tweet retweeted'''
        retweet_by = None
        real_timestamp = None
        if tweet.has_key('retweeted_status'):
            retweet_by = tweet['user']['screen_name']
            real_timestamp = tweet['created_at']
            tweet = tweet['retweeted_status']
            
        return tweet, retweet_by, real_timestamp
        
    def __print_you(self, username):
        ''' Print "you" if username is the name of the user'''
        if username == self.profile.username:
            return 'you'
        else:
            return username
    
    def __create_status(self, resp, type=UPDATE_TYPE_STD):
        tweet, retweet_by, real_timestamp = self.__get_real_tweet(resp)
        
        if tweet.has_key('user'):
            username = tweet['user']['screen_name']
            avatar = tweet['user']['profile_image_url']
        elif tweet.has_key('sender'):
            username = tweet['sender']['screen_name']
            avatar = tweet['sender']['profile_image_url']
        elif tweet.has_key('from_user'):
            username = tweet['from_user']
            avatar = tweet['profile_image_url']
        
        in_reply_to_id = None
        in_reply_to_user = None
        if (tweet.has_key('in_reply_to_status_id') and
           tweet['in_reply_to_status_id']):
            in_reply_to_id = tweet['in_reply_to_status_id']
            in_reply_to_user = tweet['in_reply_to_screen_name']
            
        fav = False
        if tweet.has_key('favorited'):
            fav = tweet['favorited']
        source = None
        if tweet.has_key('source'):
            source = tweet['source']
        
        if username.lower() == self.profile.username.lower():
            own = True
        else:
            own = False
            
        if not real_timestamp:
            real_timestamp = tweet['created_at']
        
        status = Status()
        status.id = str(tweet['id'])
        status.username = username
        status.avatar = avatar
        status.source = source
        status.text = tweet['text']
        status.in_reply_to_id = in_reply_to_id
        status.in_reply_to_user = in_reply_to_user
        status.is_favorite = fav
        status.retweet_by = retweet_by
        status.datetime = self.get_str_time(tweet['created_at'])
        status.timestamp = self.get_int_time(real_timestamp)
        status.type = type
        status.protocol = PROTOCOLS[0]
        status.is_own = own
        return status
        
    def __create_profile(self, pf):
        profile = Profile()
        profile.id = pf['id']
        profile.fullname = pf['name']
        profile.username = pf['screen_name']
        profile.avatar = pf['profile_image_url']
        profile.location = pf['location']
        profile.url = pf['url']
        profile.bio = pf['description']
        profile.following = pf['following']
        profile.followers_count = pf['followers_count']
        profile.friends_count = pf['friends_count']
        profile.statuses_count = pf['statuses_count']
        if pf.has_key('status'):
            profile.last_update = pf['status']['text']
            profile.last_update_id = pf['status']['id']
        profile.profile_link_color = ('#%s' % pf['profile_link_color']) or '#0F0F85'
        return profile
        
    def __create_list(self, ls):
        _list = List()
        _list.id = ls['id']
        _list.slug = ls['slug']
        _list.name = ls['name']
        _list.mode = ls['mode']
        _list.user = ls['user']['screen_name']
        _list.member_count = ls['member_count']
        _list.description = ls['description']
        return _list
        
    def __create_rate(self, rl):
        rate = RateLimit()
        rate.hourly_limit = rl['hourly_limit']
        rate.remaining_hits = rl['remaining_hits']
        rate.reset_time = rl['reset_time']
        rate.reset_time_in_seconds = rl['reset_time_in_seconds']
        return rate
        
    def __get_retweet_users(self, id):
        users = ''
        try:
            rts = self.http.request('%s/statuses/%s/retweeted_by' % 
                (self.apiurl, id))
            
            results = self.response_to_profiles(rts)
            if len(results) == 1:
                users = self.__print_you(results[0].username)
            else:
                length = len(results)
                limit = 2 if length > 3 else length - 1
                
                for index in range(limit):
                    users += self.__print_you(results[index].username) + ', '
                
                if length > 3:
                    tail = ' and %i others' % (length - limit)
                else:
                    tail = ' and %s' % self.__print_you(results[limit].username)
                users = users[:-2] + tail
        except Exception, exc:
            print exc
        
        return users
        
    def response_to_statuses(self, response, mute=False, type=UPDATE_TYPE_STD):
        statuses = []
        for resp in response:
            if not resp:
                continue
            status = self.__create_status(resp, type)
            if status.retweet_by and self.oauth_support:
                users = self.__get_retweet_users(status.id)
                status.retweet_by = users
            statuses.append(status)
        return statuses
        
    def response_to_profiles(self, response):
        profiles = []
        for pf in response:
            profiles.append(self.__create_profile(pf))
        return profiles
            
    def auth(self, args):
        ''' Inicio de autenticacion segura '''
        self.log.debug('Iniciando autenticacion segura')
        username = args['username']
        password = args['password']
        
        try:
            url = '%s/account/verify_credentials' % self.apiurl
            url = url.replace('http://', 'https://')
            rtn = self.http.request(url)
            self.profile = self.__create_profile(rtn)
            self.profile.password = password
            return Response(self.profile, 'profile')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        except Exception, exc:
            self.log.debug('Authentication Error: %s' % exc)
            return Response(None, 'error', _('Authentication Error'))
    
    def start_oauth(self, args):
        auth = args['auth']
        if auth['oauth-key'] != '' and auth['oauth-secret'] != '' and \
        auth['oauth-verifier'] != '':
            token = self.http.build_token(auth)
            return Response(token, 'auth-done')
        else:
            try:
                url = self.http.request_token()
                return Response(url, 'auth-token')
            except TurpialException, exc:
                return Response(None, 'error', exc.msg)
    
    def authorize_oauth_token(self, args):
        token = self.http.authorize_token(args['pin'])
        return token.key, token.secret, token.verifier #Response(token, 'auth-done')
        
    def get_timeline(self, args):
        '''Actualizando linea de tiempo'''
        self.log.debug('Descargando timeline')
        count = args['count']
        
        try:
            rtn = self.http.request('%s/statuses/home_timeline' % 
                self.apiurl, {'count': count})
            self.timeline = self.response_to_statuses(rtn)
            return Response(self.get_muted_timeline(self.timeline), 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def get_replies(self, args):
        '''Actualizando menciones'''
        self.log.debug('Descargando menciones')
        count = args['count']
        
        try:
            rtn = self.http.request('%s/statuses/mentions' % 
                self.apiurl, {'count': count})
            self.replies = self.response_to_statuses(rtn)
            return Response(self.replies, 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def get_directs(self, args):
        '''Actualizando mensajes directos'''
        self.log.debug('Descargando directos')
        count = args['count']
        
        try:
            rtn = self.http.request('%s/direct_messages' % self.apiurl, 
                {'count': count})
            self.directs = self.response_to_statuses(rtn, type=UPDATE_TYPE_DM)
            rtn = self.http.request('%s/direct_messages/sent' % self.apiurl, 
                {'count': count})
            self.directs += self.response_to_statuses(rtn, type=UPDATE_TYPE_DM)
            return Response(self.directs, 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
            
    def get_sent(self, args):
        '''Actualizando mensajes enviados'''
        self.log.debug('Descargando mis tweets')
        count = args['count']
        
        try:
            rtn = self.http.request('%s/statuses/user_timeline' % self.apiurl, 
                {'count': count})
            self.directs = self.response_to_statuses(rtn)
            return Response(self.directs, 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def get_favorites(self):
        '''Actualizando favoritos'''
        self.log.debug('Descargando favoritos')
        
        try:
            rtn = self.http.request('%s/favorites' % self.apiurl)
            self.favorites = self.response_to_statuses(rtn)
            return Response(self.favorites, 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def get_rate_limits(self):
        '''Actualizando llamdas restantes a la api'''
        try:
            rtn = self.http.request('%s/account/rate_limit_status' % 
                self.apiurl)
            return Response(self.__create_rate(rtn), 'rate')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def get_conversation(self, args):
        '''Obteniendo conversacion'''
        id = args['id']
        conversation = []
        
        self.log.debug(u'Obteniendo conversación:')
        
        while 1:
            try:
                rtn = self.http.request('%s/statuses/show' % self.apiurl, 
                    {'id': id})
            except TurpialException, exc:
                return Response(None, 'error', exc.msg)
                
            self.log.debug('--Descargado Tweet: %s' % id)
            conversation.append(rtn)
            
            if rtn['in_reply_to_status_id']:
                id = str(rtn['in_reply_to_status_id'])
            else:
                break
        
        return Response(self.response_to_statuses(conversation), 'profile')
        
    def get_friends_list(self):
        '''Descargando lista de amigos'''
        tries = 0
        count = 0
        cursor = -1
        friends = []
        
        self.log.debug('Descargando Lista de Amigos')
        while 1:
            try:
                rtn = self.http.request('%s/statuses/friends' % self.apiurl, 
                    {'cursor': cursor})
            except TurpialException, exc:
                tries += 1
                if tries < 3:
                    continue
                else:
                    return Response(None, 'error', exc.msg)
                
            for user in rtn['users']:
                friends.append(self.__create_profile(user))
                count += 1
            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
                continue
            else:
                break
        
        self.friends = friends
        self.log.debug('--Descargados %i amigos' % count)
        self.friendsloaded = True
        
    def update_profile(self, args):
        '''Actualizando perfil'''
        self.log.debug('Actualizando perfil')
        
        name = args['name']
        url = args['url']
        bio = args['bio']
        location = args['location']
        
        try:
            rtn = self.http.request('%s/account/update_profile' % self.apiurl, 
                {'name': name, 'url': url, 'location': location, 
                'description': bio})
            return Response(self.__create_profile(rtn), 'profile')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def update_status(self, args):
        '''Actualizando estado'''
        in_reply_id = args['in_reply_id']
        text = args['text']
        
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}
        self.log.debug(u'Nuevo tweet: %s' % text)
        
        try:
            rtn = self.http.request('%s/statuses/update' % self.apiurl, args)
            # Evita que se duplique el último estado del usuario
            if rtn['id'] != self.profile.last_update_id:
                status = self.__create_status(rtn)
                self._add_status(self.timeline, status)
                self.profile.last_update = rtn['text']
                self.profile.last_update_id = rtn['id']
            return Response(self.get_muted_timeline(self.timeline), 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def destroy_status(self, args):
        '''Destruyendo tweet'''
        id = args['id']
        self.log.debug('Destruyendo tweet: %s' % id)
        
        try:
            rtn = self.http.request('%s/statuses/destroy' % self.apiurl,
                {'id': id})
            self._destroy_status(str(rtn['id']))
            return (Response(self.get_muted_timeline(self.timeline), 'status'), 
                Response(self.favorites, 'status'))
        except TurpialException, exc:
            return (Response(None, 'error', exc.msg), 
                Response(None, 'error', exc.msg))
        
    def repeat(self, args):
        '''Haciendo retweet'''
        id = args['id']
        self.log.debug('Retweet: %s' % id)
        
        try:
            rtn = self.http.request('%s/statuses/retweet' % self.apiurl, args)
            users = self.__get_retweet_users(id)
            status = self.__create_status(rtn)
            status.retweet_by = users
            # FIXME: Modificar también los replies y favoritos
            self._add_status(self.timeline, status)
            return Response(self.get_muted_timeline(self.timeline), 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def mark_favorite(self, args):
        '''Marcando tweet como favorito'''
        id = args['id']
        self.log.debug('Marcando tweet como favorito: %s' % id)
        
        try:
            rtn = self.http.request('%s/favorites/create' % self.apiurl, 
                {'id': id})
            status = self.__create_status(rtn)
            self._set_status_favorite(status)
            return (Response(self.get_muted_timeline(self.timeline), 'status'), 
                Response(self.replies, 'status'),
                Response(self.favorites, 'status'))
        except TurpialException, exc:
            self.log.debug(exc)
            return (Response(None, 'error', exc.msg), 
                Response(None, 'error', exc.msg), 
                Response(None, 'error', exc.msg))
        
    def unmark_favorite(self, args):
        '''Desmarcando tweet como favorito'''
        id = args['id']
        self.log.debug('Desmarcando tweet como favorito: %s' % id)
        
        try:
            rtn = self.http.request('%s/favorites/destroy' % self.apiurl, 
                {'id': id})
            status = self.__create_status(rtn)
            self._unset_status_favorite(status)
            return (Response(self.get_muted_timeline(self.timeline), 'status'), 
                Response(self.replies, 'status'),
                Response(self.favorites, 'status'))
        except TurpialException, exc:
            return (Response(None, 'error', exc.msg), 
                Response(None, 'error', exc.msg), 
                Response(None, 'error', exc.msg))
                
    def follow(self, args):
        '''Siguiendo a un amigo'''
        user = args['user']
        self.log.debug('Siguiendo a: %s' % user)
        
        try:
            rtn = self.http.request('%s/friendships/create' % self.apiurl,
                {'screen_name': user})
            user = self.__create_profile(rtn)
            self._add_friend(user)
            return Response([self.profile, user, True], 'mixed')
        except TurpialException, exc:
            return Response([None, user, True], 'error', exc.msg)
        
    def unfollow(self, args):
        '''Dejando de seguir a un amigo'''
        user = args['user']
        self.log.debug('Dejando de seguir a: %s' % user)
        
        try:
            rtn = self.http.request('%s/friendships/destroy' % self.apiurl,
                {'screen_name': user})
            user = self.__create_profile(rtn)
            self._del_friend(user)
            return Response([self.profile, user, False], 'mixed')
        except TurpialException, exc:
            return Response(False, 'error', exc.msg)
        
    def send_direct(self, user, text):
        pass
        
    def destroy_direct(self, args):
        '''Destruyendo tweet directo'''
        id = args['id']
        self.log.debug('Destruyendo directo: %s' % id)
        
        try:
            rtn = self.http.request('%s/direct_messages/destroy' % self.apiurl,
                {'id': id})
            self._destroy_direct(str(rtn['id']))
            return Response(self.directs, 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def search(self, args):
        ''' Buscando en Twitter '''
        query = args['query']
        count = args['count']
        self.log.debug('Buscando tweets: %s' % query)
        
        try:
            rtn = self.http.request('%s/search' % self.apiurl2, 
                {'q': query, 'rpp': count})
            return Response(self.response_to_statuses(rtn['results']), 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
            
    def get_lists(self):
        ''' Obteniendo las listas del usuario '''
        tries = 0
        count = 0
        cursor = -1
        lists = []
        
        self.log.debug('Descargando Listas del usuario')
        # Descargando listas propias
        while 1:
            try:
                rtn = self.http.request('%s/%s/lists' % (self.apiurl, 
                    self.profile.username), {'cursor': cursor})
            except TurpialException, exc:
                tries += 1
                if tries < 3:
                    continue
                else:
                    return Response(None, 'error', exc.msg)
                
            for ls in rtn['lists']:
                lists.append(self.__create_list(ls))
                count += 1
            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
                continue
            else:
                break
        
        # Descargando listas a las que estás suscrito
        while 1:
            try:
                rtn = self.http.request('%s/%s/lists/subscriptions' % (self.apiurl, 
                    self.profile.username), {'cursor': cursor})
            except TurpialException, exc:
                tries += 1
                if tries < 3:
                    continue
                else:
                    return Response(None, 'error', exc.msg)
                
            for ls in rtn['lists']:
                lists.append(self.__create_list(ls))
                count += 1
            if rtn['next_cursor'] > 0:
                cursor = rtn['next_cursor']
                continue
            else:
                break
        
        self.lists = lists
        self.log.debug('--Descargadas %i listas' % count)
        return self.lists
        
    def get_list_statuses(self, args):
        '''Actualizando estados de una lista'''
        id = args['id']
        user = args['user']
        count = args['count']
        self.log.debug('Descargando lista %s' % id)
        
        try:
            rtn = self.http.request('%s/%s/lists/%s/statuses' % (self.apiurl, 
                user, id), {'per_page': count})
            statuses = self.response_to_statuses(rtn)
            return Response(self.get_muted_timeline(statuses), 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
            

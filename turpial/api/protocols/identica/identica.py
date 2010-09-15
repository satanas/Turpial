# -*- coding: utf-8 -*-

"""Implementación del protocolo Identica para Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Jun 08, 2010

from turpial.api.interfaces.protocol import Protocol
from turpial.api.interfaces.http import TurpialException
from turpial.api.protocols.identica.http import IdenticaHTTP
from turpial.api.interfaces.post import Status, Response, Profile, RateLimit


class Identica(Protocol):
    def __init__(self):
        Protocol.__init__(self, 'Identi.ca', 'http://identi.ca/api', 
            'http://identi.ca/api', 'http://identi.ca/tag', 
            'http://identi.ca/group', 'http://identi.ca')
        
        self.http = IdenticaHTTP()
        self.retweet_by_me = []
        
    def __get_real_tweet(self, tweet):
        '''Get the tweet retweeted'''
        retweet_by = None
        if tweet.has_key('retweeted_status'):
            retweet_by = tweet['user']['screen_name']
            tweet = tweet['retweeted_status']
        
        return tweet, retweet_by
        
    def __print_you(self, username):
        ''' Print "you" is username is the name of the user'''
        if username == self.profile.username:
            return 'you'
        else:
            return username
    
    def __create_status(self, resp):
        tweet, retweet_by = self.__get_real_tweet(resp)
        
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
        if tweet.has_key('in_reply_to_status_id') and \
           tweet['in_reply_to_status_id']:
            in_reply_to_id = tweet['in_reply_to_status_id']
            in_reply_to_user = tweet['in_reply_to_screen_name']
            
        fav = False
        if tweet.has_key('favorited'):
            fav = tweet['favorited']
        source = None
        if tweet.has_key('source'):
            source = tweet['source']
        
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
        status.datetime = tweet['created_at']
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
        profile.profile_link_color = pf['profile_link_color'] or '#0F0F85'
        return profile
        
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
        
    def response_to_statuses(self, response, mute=False):
        statuses = []
        for resp in response:
            status = self.__create_status(resp)
            #if status.retweet_by:
            #    users = self.__get_retweet_users(status.id)
            #    status.retweet_by = users
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
        auth = args['auth']
        protocol = args['protocol']
        
        try:
            self.http.auth(username, password, None)
            rtn = self.http.request('%s/account/verify_credentials' % 
                self.apiurl)
            self.profile = self.__create_profile(rtn)
            self.profile.password = password
            
            return Response(self.profile, 'profile'), None, None, protocol
        except TurpialException, exc:
            return Response(None, 'error', exc.msg), None, None, None
        except Exception, exc:
            self.log.debug('Authentication Error: %s' % exc)
            return Response(None, 'error', _('Authentication Error')), None, None, None
        
    def get_timeline(self, args):
        '''Actualizando linea de tiempo'''
        self.log.debug('Descargando timeline')
        count = args['count']
        
        try:
            rtn = self.http.request('%s/statuses/home_timeline' % 
                self.apiurl, {'count': count})
            self.timeline = self.response_to_statuses(rtn)
            return Response(self.get_muted_timeline(), 'status')
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
                
            for user in rtn:
                friends.append(self.__create_profile(user))
                count += 1
            break
            #if rtn['next_cursor'] > 0:
            #    cursor = rtn['next_cursor']
            #    continue
            #else:
            #    break
        
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
            args['in_reply_to_status_id'] = in_reply_id
        
        args['status'] = text
        args['source'] = 'Turpial'
        self.log.debug(u'Nuevo tweet: %s' % text)
        
        try:
            rtn = self.http.request('%s/statuses/update' % self.apiurl, args)
            status = self.__create_status(rtn)
            self._add_status(self.timeline, status)
            timeline = self.get_muted_timeline()
            return Response(timeline, 'status')
        except TurpialException, exc:
            return Response(None, 'error', exc.msg)
        
    def destroy_status(self, args):
        '''Destruyendo tweet'''
        id = args['id']
        self.to_del.append(id)
        self.log.debug('Destruyendo tweet: %s' % id)
        
        try:
            rtn = self.http.request('%s/statuses/destroy' % self.apiurl,
                {'id': id})
            
            self._destroy_status(str(rtn['id']))
            timeline = self.get_muted_timeline()
            return (Response(timeline, 'status'), 
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
            #users = self.__get_retweet_users(id)
            status = self.__create_status(rtn)
            #status.retweet_by = users
            # FIXME: Modificar también los replies y favoritos
            self._add_status(self.timeline, status)
            timeline = self.get_muted_timeline()
            return Response(timeline, 'status')
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
            timeline = self.get_muted_timeline()
            return (Response(timeline, 'status'), 
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
            timeline = self.get_muted_timeline()
            return (Response(timeline, 'status'), 
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
            self._destroy_direct(rtn['id'])
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
        return []
        
    def get_list_statuses(self, args):
        pass

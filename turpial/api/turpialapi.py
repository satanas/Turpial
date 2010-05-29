# -*- coding: utf-8 -*-

'''Modelo base basado en hilos para el Turpial'''
#
# Author: Wil Alvarez (aka Satanas)
# Dic 22, 2009

import sys
import time
import Queue
import logging
import threading
import traceback

from turpial.api.protocols.twitter import twitter
from turpial.api.interfaces.post import Response

class TurpialAPI(threading.Thread):
    '''API basica de turpial basada en hilos'''
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.setDaemon(False)
        self.log = logging.getLogger('API')
        self.queue = Queue.Queue()
        self.exit = False
        self.protocol = twitter.Twitter()
        self.log.debug('Iniciado')
        
    def __register(self, funct, args, callback):
        self.queue.put((funct, args, callback))
    
    def change_api_url(self, url):
        pass
        
    def has_oauth_support(self):
        return False
    
    def is_marked_to_fav(self, id):
        return id in self.protocol.to_fav
        
    def is_marked_to_unfav(self, id):
        return id in self.protocol.to_unfav
        
    def is_marked_to_del(self, id):
        return id in self.protocol.to_del
        
    def friends_loaded(self):
        return self.protocol.friendsloaded
        
    def is_friend(self, user):
        return self.protocol.is_friend(user)
        
    def is_fav(self, id):
        return self.protocol.is_favorite(id)
        
    '''
    def __handle_oauth(self, args, callback):
        if args['cmd'] == 'start':
            if self.has_oauth_support():
                self.client = TurpialAuthClient()
            else:
                self.client = TurpialAuthClient(api_url=self.apiurl)
            self.consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
            self.signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
            auth = args['auth']
            
            if auth['oauth-key'] != '' and auth['oauth-secret'] != '' and \
            auth['oauth-verifier'] != '':
                self.token = oauth.OAuthToken(auth['oauth-key'],
                                              auth['oauth-secret'])
                self.token.set_verifier(auth['oauth-verifier'])
                self.is_oauth = True
                args['done'](self.token.key, self.token.secret,
                             self.token.verifier)
            else:
                self.log.debug('Obtain a request token')
                oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                                           http_url=self.client.request_token_url)
                oauth_request.sign_request(self.signature_method_hmac_sha1,
                                           self.consumer, None)
                
                self.log.debug('REQUEST (via headers)')
                self.log.debug('parameters: %s' % str(oauth_request.parameters))
                try:
                    self.token = self.client.fetch_request_token(oauth_request)
                except Exception, error:
                    print "Error: %s\n%s" % (error, traceback.print_exc())
                    raise Exception
                
                self.log.debug('GOT')
                self.log.debug('key: %s' % str(self.token.key))
                self.log.debug('secret: %s' % str(self.token.secret))
                self.log.debug('callback confirmed? %s' % str(self.token.callback_confirmed))
                
                self.log.debug('Authorize the request token')
                oauth_request = oauth.OAuthRequest.from_token_and_callback(token=self.token,
                                                                           http_url=self.client.authorization_url)
                self.log.debug('REQUEST (via url query string)')
                self.log.debug('parameters: %s' % str(oauth_request.parameters))
                callback(oauth_request.to_url())
        elif args['cmd'] == 'authorize':
            pin = args['pin']
            self.log.debug('Obtain an access token')
            oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                                                       token=self.token,
                                                                       verifier=pin,
                                                                       http_url=self.client.access_token_url)
            oauth_request.sign_request(self.signature_method_hmac_sha1,
                                       self.consumer, self.token)
            self.log.debug('REQUEST (via headers)')
            self.log.debug('parameters: %s' % str(oauth_request.parameters))
            self.token = self.client.fetch_access_token(oauth_request)
            self.log.debug('GOT')
            self.log.debug('key: %s' % str(self.token.key))
            self.log.debug('secret: %s' % str(self.token.secret))
            self.is_oauth = True
            callback(self.token.key, self.token.secret, pin)
    '''
    def auth(self, username, password, callback):
        '''Inicio de autenticacion basica'''
        self.log.debug('Solicitando autenticacion basica')
        self.__register(self.protocol.auth, {'username': username, 
            'password': password}, callback)
            
    def update_timeline(self, callback, count=20):
        '''Actualizando linea de tiempo'''
        self.log.debug('Solicitando Timeline')
        self.__register(self.protocol.get_timeline, {'count': count}, callback)
    
    def update_replies(self, callback, count=20):
        '''Actualizando respuestas'''
        self.log.debug('Solicitando Replies')
        self.__register(self.protocol.get_replies, {'count': count}, callback)
        
    def update_directs(self, callback, count=20):
        '''Actualizando mensajes directos'''
        self.log.debug('Solicitando Directos')
        self.__register(self.protocol.get_directs, {'count': count}, callback)
        
    def update_favorites(self, callback):
        '''Actualizando favoritos'''
        self.log.debug('Solicitando Favoritos')
        self.__register(self.protocol.get_favorites, None, callback)
        
    def update_rate_limits(self, callback):
        self.__register(self.protocol.get_rate_limits, None, callback)
    
    """
        
    def update_status(self, text, in_reply_id, callback):
        '''Actualizando estado'''
        if in_reply_id:
            args = {'status': text, 'in_reply_to_status_id': in_reply_id}
        else:
            args = {'status': text}
        self.log.debug(u'Nuevo tweet: %s' % text)
        self.__register({'uri': '%s/statuses/update' % self.apiurl,
                         'args': args, 'tweet':True, 'add': True}, callback)
        
    def destroy_status(self, tweet_id, callback):
        self.to_del.append(tweet_id)
        self.log.debug('Destruyendo tweet: %s' % tweet_id)
        self.__register({'uri': '%s/statuses/destroy' % self.apiurl,
                         'id': tweet_id, 'args': '', 'tweet':True,
                         'del': True}, callback)
        
    def retweet(self, tweet_id, callback):
        '''Haciendo retweet'''
        self.log.debug('Retweet: %s' % tweet_id)
        self.__register({'uri': '%s/statuses/retweet' % self.apiurl,
                         'id':tweet_id, 'rt':True, 'args': ''}, callback)
        
    """
    def set_favorite(self, id, callback):
        '''Estableciendo status como favorito'''
        self.log.debug('Solicitando status como favorito: %s' % id)
        
        self.__register(self.protocol.mark_favorite, {'id': id}, callback)
        
    def unset_favorite(self, id, callback):
        '''Desmarcando status como favorito'''
        self.log.debug('Solicitando status como no favorito: %s' % id)
        
        self.__register(self.protocol.unmark_favorite, {'id': id}, callback)
        
    """
    def search_topic(self, query, callback):
        '''Buscando tweet'''
        args = {'q': query, 'rpp': 50}
        self.log.debug('Buscando tweets: %s' % query)
        self.__register({'uri': 'http://search.twitter.com/search',
                         'args': args}, callback)
        
    def update_profile(self, name, url, bio, location, callback):
        '''Actualizando perfil'''
        args = {'name': name, 'url': url, 'location': location,
                'description': bio}
        self.log.debug('Actualizando perfil')
        self.__register({'uri': '%s/account/update_profile' % self.apiurl,
                         'args': args}, callback)
    """
    def get_friends(self, callback):
        '''Descargando lista de amigos'''
        self.log.debug('Solicitando Lista de Amigos')
        self.__register(self.protocol.get_friends_list, None, callback)
        
    def get_muted_list(self):
        return self.protocol.get_muted_friends_list()
        '''
        friendsloaded:
            friends = []
            for f in self.friends:
                friends.append(f['screen_name'])
            
            return friends, self.muted_users
        else:
            return None, None
        '''
    """
            
    def follow(self, user, callback):
        '''Siguiendo a un amigo'''
        args = {'screen_name': user}
        self.log.debug('Siguiendo a: %s' % user)
        self.__register({'uri': '%s/friendships/create' % self.apiurl,
                         'args': args, 'follow': True}, callback)
        
    def unfollow(self, user, callback):
        '''Dejando de seguir a un amigo'''
        args = {'screen_name': user}
        self.log.debug('Dejando de seguir a: %s' % user)
        self.__register({'uri': '%s/friendships/destroy' % self.apiurl,
                         'args': args, 'follow': False}, callback)
        
    def mute(self, arg, callback):
        '''Actualizando usuarios silenciados'''
        if type(arg).__name__ == 'list':
            self.log.debug('Actualizando usuarios silenciados')
            self.muted_users = arg
        else:
            friends, _ = self.get_muted_list()
            if arg not in friends:
                self.log.debug('No se silencia a %s porque no es tu amigo' % arg)
            elif arg not in self.muted_users: 
                self.log.debug('Silenciando a %s' % arg)
                self.muted_users.append(arg)
        self.__register({'mute': True}, callback)
        
    def in_reply_to(self, tweet_id, callback):
        '''Buscando tweet en respuesta a'''
        self.log.debug('Buscando respuesta: %s' % tweet_id)
        self.__register({'uri': '%s/statuses/show' % self.apiurl,
                         'id': tweet_id}, callback)
    """
    def get_conversation(self, id, callback):
        '''Obteniendo conversacion'''
        self.log.debug(u'Solicitando conversación')
        self.__register(self.protocol.get_conversation, {'id': id}, callback)
        
    """
    def destroy_direct(self, tweet_id, callback):
        '''Destruyendo tweet directo'''
        self.to_del.append(tweet_id)
        self.log.debug('Destruyendo directo: %s' % tweet_id)
        self.__register({'uri': '%s/direct_messages/destroy' % self.apiurl,
                         'id': tweet_id, 'args': '', 'tweet':True,
                         'del': True}, callback)
        
    def get_single_friends_list(self):
        '''Returns a single friends list from the original twitter hash'''
        list = []
        for friend in self.friends:
            list.append(friend['screen_name'])
        return list
        
    def end_session(self):
        '''Finalizando sesion'''
        self.__register({'uri': '%s/account/end_session' % self.apiurl,
                         'args': '', 'exit': True}, None)
        
    """
    def quit(self):
        '''Definiendo la salida'''
        self.exit = True
    
    def run(self):
        '''Bloque principal de ejecucion'''
        while not self.exit:
            time.sleep(0.3)
            try:
                req = self.queue.get(False)
            except Queue.Empty:
                continue
            
            (funct, args, callback) = req
            
            # FIXME: Poner try/except
            #-------------------------
            if args:
                rtn = funct(args)
            else:
                rtn = funct()
            #-------------------------
            
            if isinstance(rtn, Response):
                callback(rtn)
            elif len(rtn) == 2:
                callback(rtn[0],rtn[1])
            elif len(rtn) == 3:
                callback(rtn[0],rtn[1],rtn[2])
            elif len(rtn) == 4:
                callback(rtn[0],rtn[1],rtn[2],rtn[3])
            
        self.log.debug('Terminado')
        return
        

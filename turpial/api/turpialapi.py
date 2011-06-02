# -*- coding: utf-8 -*-

'''Modelo base basado en hilos para el Turpial'''
#
# Author: Wil Alvarez (aka Satanas)
# Dic 22, 2009

import Queue
import logging
import threading
import traceback

from turpial.api.protocols.twitter import twitter
from turpial.api.protocols.identica import identica
from turpial.api.interfaces.post import Response
from turpial.config import PROTOCOLS

class TurpialAPI(threading.Thread):
    '''API basica de turpial basada en hilos'''
    def __init__(self):
        threading.Thread.__init__(self)
        
        self.setDaemon(False)
        self.queue = Queue.Queue()
        self.exit = False
        #self.protocol = twitter.Twitter()
        #self.protocol = identica.Identica()
        self.protocol = None
        
        self.log = logging.getLogger('API')
        self.log.debug('Iniciado')
        
    def __register(self, funct, args, callback):
        self.queue.put((funct, args, callback))
    
    def change_api_url(self, url):
        pass
    
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
    
    def auth(self, username, password, auth_info, protocol, callback):
        '''Inicio de autenticacion'''
        args = {'username': username, 'password': password, 'auth': auth_info,
            'protocol': protocol}
        self.log.debug('Solicitando autenticacion')
        if protocol == PROTOCOLS[0]:
            self.protocol = twitter.Twitter()
        elif protocol == PROTOCOLS[1]:
            self.protocol = identica.Identica()
        self.__register(self.protocol.auth, args, callback)
            
    def update_column(self, callback, count, column):
        if column.id == 'timeline':
            self.update_timeline(callback, count)
        elif column.id == 'replies':
            self.update_replies(callback, count)
        elif column.id == 'directs':
            self.update_directs(callback, count)
        elif column.id == 'sent':
            self.update_sent(callback, count)
        else:
            self.update_list(callback, column, count)
            
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
        
    def update_sent(self, callback, count=20):
        '''Actualizando mensajes enviados'''
        self.log.debug('Solicitando Mis Tweets')
        self.__register(self.protocol.get_sent, {'count': count}, callback)
        
    def update_list(self, callback, column, count=20):
        '''Actualizando lista'''
        self.log.debug('Solicitando Lista %s' % column.id)
        self.__register(self.protocol.get_list_statuses, {'count': count, 
            'id': column.id, 'user': column.user}, callback)
        
    def update_favorites(self, callback):
        '''Actualizando favoritos'''
        self.log.debug('Solicitando Favoritos')
        self.__register(self.protocol.get_favorites, None, callback)
        
    def update_rate_limits(self, callback):
        '''Actualizando limites de API'''
        self.__register(self.protocol.get_rate_limits, None, callback)
    
    def update_status(self, text, in_reply_id, callback):
        '''Actualizando estado'''
        args = {'text': text, 'in_reply_id': in_reply_id}
        self.log.debug(u'Solicitando nuevo estado: %s' % text)
        self.__register(self.protocol.update_status, args, callback)
    
    def destroy_status(self, id, callback):
        '''Destruyendo estado'''
        self.log.debug('Solicitando destrucción de estado: %s' % id)
        self.protocol.to_del.append(id)
        self.__register(self.protocol.destroy_status, {'id': id}, callback)
        
    def destroy_direct(self, id, callback):
        '''Destruyendo directo'''
        self.log.debug('Solicitando destrucción de directo: %s' % id)
        self.protocol.to_del.append(id)
        self.__register(self.protocol.destroy_direct, {'id': id}, callback)
        
    def repeat(self, id, callback):
        '''Repitiendo status a todos los contactos'''
        self.log.debug('Solicitando repetición de status: %s' % id)
        self.__register(self.protocol.repeat, {'id': id}, callback)
        
    def set_favorite(self, id, callback):
        '''Estableciendo status como favorito'''
        self.log.debug('Solicitando status como favorito: %s' % id)
        self.protocol.to_fav.append(id)
        self.__register(self.protocol.mark_favorite, {'id': id}, callback)
        
    def unset_favorite(self, id, callback):
        '''Desmarcando status como favorito'''
        self.log.debug('Solicitando status como no favorito: %s' % id)
        self.protocol.to_unfav.append(id)
        self.__register(self.protocol.unmark_favorite, {'id': id}, callback)
        
    def search(self, query, callback):
        '''Buscando tweet'''
        args = {'query': query, 'count': 60}
        self.log.debug('Solicitando búsqueda: %s' % query)
        self.__register(self.protocol.search, args, callback)
    
    def update_profile(self, name, url, bio, location, callback):
        '''Actualizando perfil'''
        self.log.debug('Solicitando actualización de perfil')
        args = {'name': name, 'url': url, 'location': location, 'bio': bio}
        self.__register(self.protocol.update_profile, args, callback)
    
    def get_friends(self):
        '''Descargando lista de amigos'''
        self.log.debug('Solicitando Lista de Amigos')
        self.__register(self.protocol.get_friends_list, None, None)
        
    def get_muted_list(self):
        return self.protocol.get_muted_friends_list()
        
    def get_single_friends_list(self):
        '''Returns a single friends list from the original twitter hash'''
        if self.protocol.friendsloaded:
            list = []
            for friend in self.protocol.friends:
                list.append(friend.username)
            list.sort()
        else:
            list = None
        return list
    
    def follow(self, user, callback):
        '''Siguiendo a un amigo'''
        args = {'user': user}
        self.log.debug('Solicitando seguir a: %s' % user)
        self.__register(self.protocol.follow, args, callback)
        
    def unfollow(self, user, callback):
        '''Dejando de seguir a un amigo'''
        args = {'user': user}
        self.log.debug('Solicitando dejar de seguir a: %s' % user)
        self.__register(self.protocol.unfollow, args, callback)
    
    def mute(self, arg, callback):
        '''Actualizando usuarios silenciados'''
        self.log.debug('Solicitando silenciar')
        self.__register(self.protocol.mute, {'arg': arg}, callback)
        
    def get_conversation(self, id, callback):
        '''Obteniendo conversacion'''
        self.log.debug(u'Solicitando conversación')
        self.__register(self.protocol.get_conversation, {'id': id}, callback)
        
    def get_lists(self):
        if len(self.protocol.lists) <= 0:
            return self.protocol.get_lists()
        else:
            return self.protocol.lists
    
    def quit(self):
        '''Definiendo la salida'''
        self.log.debug('Saliendo')
        self.exit = True
    
    def run(self):
        '''Bloque principal de ejecucion'''
        while not self.exit:
            try:
                req = self.queue.get(True, 0.3)
            except Queue.Empty:
                continue
            except:
                continue
            
            (funct, args, callback) = req
            
            # FIXME: Poner try/except
            #-------------------------
            if args:
                rtn = funct(args)
            else:
                rtn = funct()
            #-------------------------
            
            # No procesar el resultado de la solicitud si está de salida
            if self.exit:
                self.queue.task_done()
                break
            
            if not callback:
                pass
            elif isinstance(rtn, Response):
                callback(rtn)
            elif len(rtn) == 2:
                callback(rtn[0],rtn[1])
            elif len(rtn) == 3:
                callback(rtn[0],rtn[1],rtn[2])
            elif len(rtn) == 4:
                callback(rtn[0],rtn[1],rtn[2],rtn[3])
            
            self.queue.task_done()
            
        self.log.debug('Terminado')
        return
        

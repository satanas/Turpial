# -*- coding: utf-8 -*-

"""Módulo genérico para implementar protocolos de microblogging en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import logging

class Protocol:
    ''' Clase que define las funciones básicas que debe implementar cualquier
    protocolo de microblogging para Turpial '''
    def __init__(self):
        self.__timeline = []
        self.__replies = []
        self.__directs = []
        self.__favorites = []
        self.__friends = []
        self.__muted_users = []
        
        self.profile = None
        self.friendsloaded = False
        self.conversation = []
        
        self.to_fav = []
        self.to_unfav = []
        self.to_del = []
        
        self.log = logging.getLogger('Protocol')
        self.log.debug('Iniciado')
        
    # ------------------------------------------------------------
    # Common methods to all protocols
    # ------------------------------------------------------------
    
    # Status related functions
    # ------------------------------------------------------------
    def _find_status_by_id(self, from_arr, id):
        for sta in from_arr:
            if sta.id == id:
                return sta
        return None
        
    def _add_status(self, to_arr, status):
        ''' Agrega un status a cualquiera de los arreglos '''
        if status is None: 
            return
        
        if self._find_status_by_id(to_arr, status.id):
            self.log.debug('--El status %s ya existe. No se agrega' % sta.id)
            return
        
        to_arr.insert(0, status)
        self.log.debug('--Agregado status %s' % status.id)
        
    def _del_status(self, from_arr, id):
        ''' Borra un status de cualquiera de los arreglos '''
        if status is None: 
            return
        
        item = self._find_status_by_id(from_arr, status.id)
        if item:
            from_arr.insert(item)
            self.log.debug('--Removido status %s' % id)
        else:
            self.log.debug('--El status %s no existe. No se remueve' % id)
            
    def _fav_status(self, from_arr, id, fav):
        ''' Establece como favorito un status de cualquiera de los arreglos '''
        if status is None: 
            return
        
        item = self._find_status_by_id(from_arr, status.id)
        if item:
            item.favorite = fav
            self.log.debug('--Cambiado status %s' % id)
        else:
            self.log.debug('--El status %s no existe. No se cambia' % id)
            
    # -------------------------------------------------------------
    
    def _get_single_friends_list(self):
        ''' Retorna un arreglo simple de nicks de todos los amigos del usuario 
        o retorna None si aún no se han cargado '''
        single_list = []
        if self.friendsloaded:
            for friend in self.__friends:
                single_list.append(friend.screen_name)
            return single_list
        else:
            return None
        
    def _set_status_favorite(self, status):
        if status is None:
            return
        
        self.to_fav.remove(status.id)
        self._add_status(self.__favorite, status)
        self._fav_status(self.__timeline, status.id, True)
        self._fav_status(self.__replies, status.id, True)
            
        #TODO: Marcar en las listas
        
        self.log.debug('Marcado status %s como favorito' % id)
        
    def _unset_status_favorite(self, status):
        if status is None:
            return
            
        self.to_unfav.remove(status.id)
        self._del_status(self.__favorite, status)
        self._fav_status(self.__timeline, status.id, False)
        self._fav_status(self.__replies, status.id, False)
            
        #TODO: Desmarcar en las listas
        
        self.log.debug('Desmarcado status %s como favorito' % id)
        
    def _destroy_status(self, id):
        self._del_status(self.__timeline, id)
        self._del_status(self.__favorite, id)
        self._del_status(self.__directs, id)
        
    def prepare_status_to_del(self, id):
        self.to_del.append(id)
        
    def prepare_status_to_fav(self, id):
        self.to_fav.append(id)
        
    def prepare_status_to_unfav(self, id):
        self.to_unfav.append(id)
        
    def mute_by_user(self, user):
        if not self.is_friend(user):
            self.log.debug('No se silencia a %s porque no es tu amigo' % user)
            return
        
        if self.is_muted(user):
            self.log.debug('Ya %s esta silenciado. No se hace nada' % user)
        else:
            self.log.debug('Silenciando a %s' % user)
            self.muted_users.append(user)
        
    def unmute_by_user(self, user):
        if not self.is_friend(user):
            self.log.debug('No se revela a %s porque no es tu amigo' % user)
            return
        
        if not self.is_muted(user):
            self.log.debug('Ya %s esta revelado. No se hace nada' % user)
        else:
            self.log.debug('Revelando a %s' % user)
            self.muted_users.remove(user)
            
    def mute_by_list(self, list):
        self.log.debug('Silenciando por lista')
        self.muted_users = list
            
    def is_friend(self, user):
        for friend in self.__friends:
            if friend.screen_name == user:
                return True
        return False
        
    def is_muted(self, user):
        return user in self.__muted_users
        
    def is_favorite(self, id):
        for sta in self.__favorites:
            if sta.id == id:
                return sta.favorite
        return False
    
    # ------------------------------------------------------------
    # HTTP related methods to be overwritten
    # ------------------------------------------------------------
    
    def auth(self, username, password):
        raise NotImplemented
        
    def get__timeline(self, count):
        raise NotImplemented
        
    def get__replies(self, count):
        raise NotImplemented
        
    def get__directs(self, count):
        raise NotImplemented
        
    def get__favorites(self, count):
        raise NotImplemented
        
    def get_rate_limits(self):
        raise NotImplemented
        
    def get_conversation(self):
        raise NotImplemented
        
    def get_friends_list(self):
        raise NotImplemented
        
    def update_profile(self, name, url, bio, location):
        raise NotImplemented
        
    def update_status(self, in_reply_to_id):
        raise NotImplemented
        
    def destroy_status(self, id):
        ''' Implement this function in this way:
        
        self.prepare_status_to_del(id)
        # All the dirty work goes here
        self._destroy_status(id)
        '''
        raise NotImplemented
        
    def repeat(self, id):
        raise NotImplemented
        
    def mark_favorite(self, id):
        ''' Implement this function in this way:
        
        self.prepare_status_to_fav(id)
        # All the dirty work goes here
        self._set_status_favorite(id)
        '''
        raise NotImplemented
        
    def unmark_favorite(self, id):
        ''' Implement this function in this way:
        
        self.prepare_status_to_unfav(id)
        # All the dirty work goes here
        self._unset_status_favorite(id)
        '''
        raise NotImplemented
        
    def follow(self, user):
        raise NotImplemented
        
    def unfollow(self, user):
        raise NotImplemented
        
    def follow(self, user):
        raise NotImplemented
        
    def send_direct(self, user, text):
        raise NotImplemented
        
    def destroy_direct(self, id):
        ''' Implement this function in this way:
        
        self.prepare_status_to_del(id)
        # All the dirty work goes here
        self._destroy_status(id)
        '''
        raise NotImplemented
        
    def search(self, query):
        raise NotImplemented

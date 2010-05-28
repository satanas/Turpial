# -*- coding: utf-8 -*-

"""Módulo genérico para implementar protocolos de microblogging en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import logging

class Protocol:
    ''' Clase que define las funciones básicas que debe implementar cualquier
    protocolo de microblogging para Turpial '''
    def __init__(self, name, apiurl='', apiurl2=''):
        self.timeline = []
        self.replies = []
        self.directs = []
        self.favorites = []
        self.friends = []
        self.__muted_users = []
        
        self.apiurl = apiurl
        self.apiurl2 = apiurl2
        self.profile = None
        self.friendsloaded = False
        
        self.to_fav = []
        self.to_unfav = []
        self.to_del = []
        
        self.log = logging.getLogger(name)
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
    
    def _add_friend(self, user):
        exist = False
        for friend in self.friends:
            if user.username == friend.username:
                exist = True
        
        if not exist: 
            self.friends.insert(0, user)
            self.profile.friends_count += 1
            
    def _del_friend(self, id):
        item = None
        for friend in self.friends:
            if id == user.id:
                item = friend
                break
        if item: 
            self.friends.remove(item)
            self.profile.friends_count -= 1
            
    def _get_single_friends_list(self):
        ''' Retorna un arreglo simple de nicks de todos los amigos del usuario 
        o retorna None si aún no se han cargado '''
        single_list = []
        if self.friendsloaded:
            for friend in self.friends:
                single_list.append(friend.screen_name)
            return single_list
        else:
            return None
        
    def _set_status_favorite(self, status):
        if status is None:
            return
        
        self.to_fav.remove(status.id)
        self._add_status(self.favorites, status)
        self._fav_status(self.timeline, status.id, True)
        self._fav_status(self.replies, status.id, True)
            
        #TODO: Marcar en las listas
        
        self.log.debug('Marcado status %s como favorito' % id)
        
    def _unset_status_favorite(self, status):
        if status is None:
            return
            
        self.to_unfav.remove(status.id)
        self._del_status(self.favorites, status)
        self._fav_status(self.timeline, status.id, False)
        self._fav_status(self.replies, status.id, False)
            
        #TODO: Desmarcar en las listas
        
        self.log.debug('Desmarcado status %s como favorito' % id)
        
    def _destroy_status(self, id):
        self._del_status(self.timeline, id)
        self._del_status(self.favorites, id)
        self._del_status(self.directs, id)
        
    def _get_muted_timeline(self):
        timeline = []
        for tweet in self.timeline:
            if not self.is_muted(tweet.username):
                timeline.append(tweet)
        
        return timeline
        
    def change_api_url(self, new_url):
        if new_url == '': 
            return
        self.log.debug('Cambiada la API URL a %s' % new_url)
        self.apiurl = new_url
        
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
        for friend in self.friends:
            if friend.username == user:
                return True
        return False
        
    def is_muted(self, user):
        return user in self.__muted_users
        
    def is_favorite(self, id):
        for sta in self.favorites:
            if sta.id == id:
                return sta.favorite
        return False
    
    # ------------------------------------------------------------
    # HTTP related methods to be overwritten
    # ------------------------------------------------------------
    
    def response_to_statuses(self, response, mute=False):
        ''' Take the server response and transform into an array of Status 
        objects inside a Response object '''
        raise NotImplemented
        
    def response_to_profiles(self, response):
        ''' Take the server response and transform into an array of Profile 
        objects inside a Response object '''
        raise NotImplemented
        
    def auth(self, username, password):
        raise NotImplemented
        
    def get_timeline(self, count):
        ''' 
        Fetch the timeline from the server 
        Returns: a Response object with self.timeline
        '''
        raise NotImplemented
        
    def get_replies(self, count):
        ''' 
        Fetch the mentions from the server 
        Returns: a Response object with self.replies
        '''
        raise NotImplemented
        
    def get_directs(self, count):
        ''' 
        Fetch the directs from the server 
        Returns: a Response object with self.directs
        '''
        raise NotImplemented
        
    def get_favorites(self, count):
        ''' 
        Fetch the favorites from the server 
        Returns: a Response object with self.favorites
        '''
        raise NotImplemented
        
    def get_rate_limits(self):
        ''' 
        Fetch the rate limits from API 
        Returns: a Response object with a RateLimit
        '''
        raise NotImplemented
        
    def get_conversation(self, id):
        ''' 
        Fetch the whole conversation from a single status
        Returns: a Response object of statuses
        '''
        raise NotImplemented
        
    def get_friends_list(self):
        ''' 
        Fetch the whole friends list
        Returns: a Response object of profiles
        '''
        raise NotImplemented
        
    def update_profile(self, name, url, bio, location):
        ''' 
        Update the user profile
        Returns: a Response object with the user profile
        '''
        raise NotImplemented
        
    def update_status(self, in_reply_to_id):
        ''' 
        Post an update
        Returns: a Response object with the posted status
        '''
        raise NotImplemented
        
    def destroy_status(self, id):
        ''' 
        Destroy a posted update
        Returns: four Response object with self.timeline, self.favorites
        
        Implement this function in this way:
        
        self.to_del.append(id)
        # All the dirty work goes here
        self._destroy_status(id)
        '''
        raise NotImplemented
        
    def repeat(self, id):
        ''' 
        Repeat to all your friends an update posted by somebody
        Returns: a Response object with self.timeline
        '''
        raise NotImplemented
        
    def mark_favorite(self, id):
        ''' 
        Mark an update as favorite
        Returns: three Response object with self.timeline, self.replies,
        self.favorites
        
        Implement this function in this way:
        
        self.to_fav.append(id)
        # All the dirty work goes here
        self._set_status_favorite(id)
        '''
        raise NotImplemented
        
    def unmark_favorite(self, id):
        ''' 
        Unmark an update as favorite
        Returns: three Response object with self.timeline, self.replies,
        self.favorites
        
        Implement this function in this way:
        
        self.to_unfav.append(id)
        # All the dirty work goes here
        self._unset_status_favorite(id)
        '''
        raise NotImplemented
        
    def follow(self, user):
        ''' 
        Follow somebody
        Returns: four objects: single_friend_list, self.profile, user and True
        '''
        raise NotImplemented
        
    def unfollow(self, user):
        ''' 
        Unfollow somebody
        Returns: four objects: single_friend_list, self.profile, user and False
        '''
        raise NotImplemented
        
    def send_direct(self, user, text):
        # FIXME: Implementar
        #raise NotImplemented
        pass
        
    def destroy_direct(self, id):
        ''' 
        Destroy a direct message
        Returns: a Response object with self.directs
        
        Implement this function in this way:
        
        self.to_del.append(id)
        # All the dirty work goes here
        self._destroy_status(id)
        '''
        raise NotImplemented
        
    def search(self, query, count):
        ''' 
        Execute a query in server
        Returns: a Response object with query results
        '''
        raise NotImplemented

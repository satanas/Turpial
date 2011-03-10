# -*- coding: utf-8 -*-

"""Módulo genérico para implementar protocolos de microblogging en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

import time
import logging
import datetime

from turpial.api.interfaces.post import Response

class Protocol:
    ''' Clase que define las funciones básicas que debe implementar cualquier
    protocolo de microblogging para Turpial '''
    def __init__(self, name, apiurl='', apiurl2='', tags_url=None, 
        groups_url=None, profiles_url=None):
        self.timeline = []
        self.replies = []
        self.directs = []
        self.favorites = []
        self.friends = []
        self.lists = [] #Posiblemente se use más adelante
        self.muted_users = []
        
        self.apiurl = apiurl
        self.apiurl2 = apiurl2
        self.profile = None
        self.friendsloaded = False
        
        self.tags_url = tags_url
        self.groups_url = groups_url
        self.profiles_url = profiles_url
        
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
        id = str(id)
        for sta in from_arr:
            if sta.id == id:
                return sta
        return None
        
    def _add_status(self, to_arr, status):
        ''' Agrega un status a cualquiera de los arreglos '''
        if status is None: 
            return
        
        item = self._find_status_by_id(to_arr, status.id)
        if item:
            self.log.debug('--El status %s ya existe. Se edita' % status.id)
            index = to_arr.index(item)
            to_arr[index] = status
        else:
            self.log.debug('--Agregado status %s' % status.id)
            to_arr.insert(0, status)
    
    def _del_status(self, from_arr, id):
        ''' Borra un status de cualquiera de los arreglos '''
        item = self._find_status_by_id(from_arr, id)
        if item:
            from_arr.remove(item)
            self.log.debug('--Removido status %s' % id)
        else:
            self.log.debug('--El status %s no existe. No se borra' % id)
            
    def _fav_status(self, from_arr, status, fav):
        ''' Establece como favorito un status de cualquiera de los arreglos '''
        item = self._find_status_by_id(from_arr, status.id)
        if item:
            status.favorite = fav
            index = from_arr.index(item)
            from_arr[index] = status
            self.log.debug('--Cambiado status %s' % status.id)
        else:
            self.log.debug('--El status %s no existe. No se cambia' % status.id)
            
    # -------------------------------------------------------------
    
    def _add_friend(self, user):
        exist = False
        for friend in self.friends:
            if user.username == friend.username:
                exist = True
                break
        
        if not exist: 
            self.log.debug('Agregado %s a la lista de amigos' % user.username)
            self.friends.insert(0, user)
            self.profile.friends_count += 1
            
    def _del_friend(self, id):
        item = None
        for friend in self.friends:
            if id == friend.id:
                item = friend
                break
        if item: 
            self.log.debug('Removido %s de la lista de amigos' % item.username)
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
        self._add_status(self.favorites, status)
        self._fav_status(self.timeline, status, True)
        self._fav_status(self.replies, status, True)
        try:
            self.to_fav.remove(status.id)
            self.log.debug('Marcado status %s como favorito' % status.id)
        except:
            self.log.debug('El status %s ha desaparecido' % status.id)
        
    def _unset_status_favorite(self, status):
        self._del_status(self.favorites, status.id)
        self._fav_status(self.timeline, status, False)
        self._fav_status(self.replies, status, False)
        try:
            self.to_unfav.remove(status.id)
            self.log.debug('Desmarcado status %s como favorito' % status.id)
        except:
            self.log.debug('El status %s ha desaparecido' % status.id)
        
    def _destroy_status(self, id):
        self._del_status(self.timeline, id)
        self._del_status(self.favorites, id)
        self.to_del.remove(id)
        
    def _destroy_direct(self, id):
        self._del_status(self.directs, id)
        self.to_del.remove(id)
        
    def _change_api_url(self, new_url):
        if new_url == '': 
            return
        self.log.debug('Cambiada la API URL a %s' % new_url)
        self.apiurl = new_url
        
    def _mute_by_user(self, user):
        if not self.is_friend(user):
            self.log.debug('No se silencia a %s porque no es tu amigo' % user)
            return
        
        if self.is_muted(user):
            self.log.debug('Ya %s esta silenciado. No se hace nada' % user)
        else:
            self.log.debug('Silenciando a %s' % user)
            self.muted_users.append(user)
        
    def _unmute_by_user(self, user):
        if not self.is_friend(user):
            self.log.debug('No se revela a %s porque no es tu amigo' % user)
            return
        
        if not self.is_muted(user):
            self.log.debug('Ya %s esta revelado. No se hace nada' % user)
        else:
            self.log.debug('Revelando a %s' % user)
            self.muted_users.remove(user)
            
    def _mute_by_list(self, list):
        self.log.debug('Silenciando por lista')
        self.muted_users = list
        
    def get_muted_friends_list(self):
        ''' Retorna la lista de nicks silenciados o retorna None si aún no se 
        ha cargado la lista de amigos'''
        if self.friendsloaded:
            return self.muted_users
        else:
            return None
    
    def get_muted_timeline(self, statuses):
        timeline = []
        for tweet in statuses:
            if not self.is_muted(tweet.username):
                timeline.append(tweet)
        
        return timeline
            
    def is_friend(self, user):
        for friend in self.friends:
            if friend.username == user:
                return True
        return False
        
    def is_muted(self, user):
        return user in self.muted_users
        
    def is_favorite(self, id):
        for sta in self.timeline:
            if not sta:
                continue
            if sta.id == id:
                return sta.is_favorite
        for sta in self.replies:
            if not sta:
                continue
            if sta.id == id:
                return sta.is_favorite
        for sta in self.favorites:
            if not sta:
                continue
            if sta.id == id:
                return sta.is_favorite
        return False
    
    def mute(self, args):
        arg = args['arg']
        print "protocols.py: ", arg, type(arg).__name__
        if type(arg).__name__ == 'list':
            self._mute_by_list(arg)
        else:
            self._mute_by_user(arg)
        
        return (Response(self.get_muted_timeline(self.timeline), 'status'), 
                Response(self.get_muted_timeline(self.replies), 'status'),
                Response(self.get_muted_timeline(self.favorites), 'status'))
    
    # ------------------------------------------------------------
    # Time related methods. Overwrite if necesary
    # ------------------------------------------------------------
    def convert_time(self, str_datetime):
        ''' Take the date/time and convert it into Unix time'''
        # Tue Mar 13 00:12:41 +0000 2007 -> Tweets normales
        # Wed, 08 Apr 2009 19:22:10 +0000 -> Busquedas
        month_names = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
            'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        date_info = str_datetime.split()
        
        if date_info[1] in month_names:
            month = month_names.index(date_info[1])
            day = int(date_info[2])
            year = int(date_info[5])
            time_info = date_info[3].split(':')
        else:
            month = month_names.index(date_info[2])
            day = int(date_info[1])
            year = int(date_info[3])
            time_info = date_info[4].split(':')
            
        hour = int(time_info[0])
        minute = int(time_info[1])
        second = int(time_info[2])
        
        d = datetime.datetime(year, month, day, hour, minute, second)
        
        i_hate_timezones = time.timezone
        if (time.daylight):
            i_hate_timezones = time.altzone
        
        dt = datetime.datetime(*d.timetuple()[:-3]) - \
             datetime.timedelta(seconds=i_hate_timezones)
        return dt.timetuple()
        
    def get_str_time(self, strdate):
        t = self.convert_time(strdate)
        return time.strftime('%b %d, %I:%M %p', t)
        
    def get_int_time(self, strdate):
        t = self.convert_time(strdate)
        return time.mktime(t)
    
    # ------------------------------------------------------------
    # HTTP related methods to be overwritten
    # ------------------------------------------------------------
    def response_to_statuses(self, response, mute=False):
        ''' Take the server response and transform into an array of Status 
        objects inside a Response object '''
        raise NotImplementedError
        
    def response_to_profiles(self, response):
        ''' Take the server response and transform into an array of Profile 
        objects inside a Response object '''
        raise NotImplementedError
        
    def auth(self, username, password):
        raise NotImplementedError
        
    def get_timeline(self, count):
        ''' 
        Fetch the timeline from the server 
        Returns: a Response object with self.timeline
        '''
        raise NotImplementedError
        
    def get_replies(self, count):
        ''' 
        Fetch the mentions from the server 
        Returns: a Response object with self.replies
        '''
        raise NotImplementedError
        
    def get_directs(self, count):
        ''' 
        Fetch the directs from the server 
        Returns: a Response object with self.directs
        '''
        raise NotImplementedError
        
    def get_sent(self, count):
        ''' 
        Fetch the sent messages from the server 
        Returns: a Response object with self.sent
        '''
        raise NotImplementedError
        
    def get_favorites(self, count):
        ''' 
        Fetch the favorites from the server 
        Returns: a Response object with self.favorites
        '''
        raise NotImplementedError
        
    def get_rate_limits(self):
        ''' 
        Fetch the rate limits from API 
        Returns: a Response object with a RateLimit
        '''
        raise NotImplementedError
        
    def get_conversation(self, id):
        ''' 
        Fetch the whole conversation from a single status
        Returns: a Response object of statuses
        '''
        raise NotImplementedError
        
    def get_friends_list(self):
        ''' 
        Fetch the whole friends list
        Returns: a Response object of profiles
        '''
        raise NotImplementedError
        
    def update_profile(self, name, url, bio, location):
        ''' 
        Update the user profile
        Returns: a Response object with the user profile
        '''
        raise NotImplementedError
        
    def update_status(self, in_reply_to_id):
        ''' 
        Post an update
        Returns: a Response object with the posted status
        '''
        raise NotImplementedError
        
    def destroy_status(self, id):
        ''' 
        Destroy a posted update
        Returns: four Response object with self.timeline, self.favorites
        
        Implement this function in this way:
        
        self.to_del.append(id)
        # All the dirty work goes here
        self._destroy_status(id)
        '''
        raise NotImplementedError
        
    def repeat(self, id):
        ''' 
        Repeat to all your friends an update posted by somebody
        Returns: a Response object with self.timeline
        '''
        raise NotImplementedError
        
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
        raise NotImplementedError
        
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
        raise NotImplementedError
        
    def follow(self, user):
        ''' 
        Follow somebody
        Returns: four objects: single_friend_list, self.profile, user and True
        '''
        raise NotImplementedError
        
    def unfollow(self, user):
        ''' 
        Unfollow somebody
        Returns: four objects: single_friend_list, self.profile, user and False
        '''
        raise NotImplementedError
        
    def send_direct(self, user, text):
        # FIXME: Implementar
        #raise NotImplementedError
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
        raise NotImplementedError
        
    def search(self, query, count):
        ''' 
        Execute a query in server
        Returns: a Response object with query results
        '''
        raise NotImplementedError
        
    def get_lists(self):
        ''' 
        Fetch all lists for the user in that protocol
        Returns: a Response object with query results
        '''
        raise NotImplementedError
        
    def get_list_statuses(self, args):
        ''' 
        Fetch all statuses for a specific list
        Returns: a Response object with query results
        '''
        raise NotImplementedError

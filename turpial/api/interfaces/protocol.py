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
        
    def 
        
    def mute_by_user(self, user):
        friends = self.get_muted_list()
        if user not in friends:
            self.log.debug('No se silencia a %s porque no es tu amigo' % user)
        elif user not in self.muted_users: 
            self.log.debug('Silenciando a %s' % user)
            self.muted_users.append(user)
        
    def mute_by_list(self, list):
        self.log.debug('Silenciando por lista')
        self.muted_users = list
        
    def unmute_by_user(self, user):
        friends = self.get_muted_list()
        if user not in friends:
            self.log.debug('No se revela a %s porque no es tu amigo' % user)
        elif user in self.muted_users: 
            self.log.debug('Revelando a %s' % user)
            self.muted_users.remove(user)
        
    def auth(self, username, password):
        raise NotImplemented
        
    def get_timeline(self, count):
        raise NotImplemented
        
    def get_replies(self, count):
        raise NotImplemented
        
    def get_directs(self, count):
        raise NotImplemented
        
    def get_favorites(self, count):
        raise NotImplemented
        
    def get_rate_limits(self):
        raise NotImplemented
        
    def get_conversation(self):
        raise NotImplemented
        
    def get_friends_list(self):
        raise NotImplemented
        
    def get_muted_list(self):
        ''' Retorna un arreglo de nicks de todos los amigos o retorna None si
        aún no se han cargado  '''
        raise NotImplemented
        
    def update_profile(self, name, url, bio, location):
        raise NotImplemented
        
    def update_status(self, in_reply_to_id):
        raise NotImplemented
        
    def destroy_status(self, id):
        raise NotImplemented
        
    def repeat(self, id):
        raise NotImplemented
        
    def mark_favorite(self, id):
        raise NotImplemented
        
    def unmark_favorite(self, id):
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
        raise NotImplemented
        
    def is_friend(self, user):
        raise NotImplemented
        
    def is_favorite(self, id):
        raise NotImplemented
        
    def search(self, query):
        raise NotImplemented

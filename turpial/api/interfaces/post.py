# -*- coding: utf-8 -*-

"""Módulo genérico para manejar los post de microblogging en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

class Status:
    def __init__(self):
        self.id = None
        self.text = None
        self.author = None
        self.avatar = None
        self.source = None
        self.timestamp = None
        self.in_reply_to_id = None
        self.in_reply_to_user = None
        self.is_favorite = False
        self.retweeted_by = None
        self.datetime = 0

class Response:
    def __init__(self):
        self.items = []
        self.error = None

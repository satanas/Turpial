# -*- coding: utf-8 -*-

# Base class for all the Turpial interfaces
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import logging

class Base:
    '''Parent class for every UI interface'''
    def __init__(self, core):
        self.core = core
        self.log = logging.getLogger('UI')
        self.log.debug('Started')
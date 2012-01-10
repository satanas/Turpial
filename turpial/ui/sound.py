# -*- coding: utf-8 -*-

""" Base class for Turpial sounds"""
#
# Author: Wil Alvarez (aka Satanas)
# Ene 08, 2010

import os
import logging
import platform

DRIVER = None
if platform.system() == 'Windows':
    DRIVER = 'Windows'
elif platform.system() == 'Linux':
    import gst
    DRIVER = 'Linux'

class Sound:
    def __init__(self, disable=False):
        logging.basicConfig(level=logging.DEBUG)
        self.log = logging.getLogger('Sound')
        self.disable = disable
        if self.disable:
            self.log.debug('Disabled. No sounds')
            return
            
        global DRIVER
        if DRIVER == 'Windows':
            pass
        elif DRIVER == 'Linux':
            self.player = gst.element_factory_make("playbin2", "player")
            bus = self.player.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self.__on_gst_message)
        self.log.debug('Started with driver %s' % DRIVER)
    
    def __on_gst_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            self.log.debug('%s. %s' % (err, debug))
        
    def disable(self, value):
        self.disable = value
    
    def login(self):
        self.play('cambur_pinton.ogg')
        
    def updates(self):
        self.play('turpial.ogg')
        
    def replies(self):
        self.play('mencion3.ogg')
        
    def directs(self):
        self.play('mencion2.ogg')
    
    # ------------------------------------------------------------
    # This method must be overwritten for each UI if necessary
    # ------------------------------------------------------------
    
    def play(self, filename):
        if self.disable:
            return
        
        filepath = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', 'data', 'sounds', filename))
        global DRIVER
        if DRIVER == 'Windows':
            pass
        elif DRIVER == 'Linux':
            self.player.set_property("uri", "file://" + filepath)
            self.player.set_state(gst.STATE_PLAYING)

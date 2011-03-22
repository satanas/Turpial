# -*- coding: utf-8 -*-

"""Clase para reproducir sonidos en múltiples plataformas en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Ene 08, 2010

import os
import logging
import platform
import traceback

import pygst
pygst.require('0.10')
import gst

class Sound:
    def __init__(self, disable):
        self.sound = False
        self.log = logging.getLogger('Sound')
        self.disable = disable
        if self.disable:
            self.log.debug('Módulo deshabilitado')
            return

        try:
            # Create the player and a fakesink for video
            self.player = gst.element_factory_make('playbin2', 'player')
            fakesink = gst.element_factory_make('fakesink', 'fakesink')
            self.player.set_property('video-sink', fakesink)
            # Set the player message bus
            bus = self.player.get_bus()
            bus.add_signal_watch()
            bus.connect('message', self.on_message)
            self.log.debug('GStreamer inicializado...')
            self.sound = True
        except Exception, exc:
            self.log.debug(traceback.print_exc())
            self.sound = False

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()
            self.log.debug("Error: %s" % err, debug)

    def play(self, filename):
        if self.disable:
            self.log.debug('Módulo deshabilitado. No hay sonidos')
            return
        path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            'data', 'sounds', filename))

        if not self.sound:
            return

        self.player.set_property('uri', 'file://' + path)
        self.player.set_state(gst.STATE_PLAYING)

    def login(self):
        self.play('cambur_pinton.ogg')

    def tweets(self):
        self.play('turpial.ogg')

    def replies(self):
        self.play('mencion3.ogg')

    def directs(self):
        self.play('mencion2.ogg')

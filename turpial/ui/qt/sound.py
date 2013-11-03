# -*- coding: utf-8 -*-

# Base class for Turpial sound module using Qt"""

import os

from PyQt4.phonon import Phonon

class SoundSystem:
    def __init__(self, sounds_path, disable=False):
        self.sounds_path = sounds_path
        self.activate()
        self.disable = disable
        self.startup_sound = Phonon.createPlayer(Phonon.MusicCategory,
            Phonon.MediaSource(os.path.join(self.sounds_path, 'startup.ogg')))
        self.notif1_sound = Phonon.createPlayer(Phonon.MusicCategory,
            Phonon.MediaSource(os.path.join(self.sounds_path, 'notification-1.ogg')))
        self.notif2_sound = Phonon.createPlayer(Phonon.MusicCategory,
            Phonon.MediaSource(os.path.join(self.sounds_path, 'notification-2.ogg')))

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def startup(self):
        self.startup_sound.play()

    def notification_1(self):
        self.notif1_sound.play()

    def notification_2(self):
        self.notif2_sound.play()

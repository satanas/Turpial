# -*- coding: utf-8 -*-

# Base class for Turpial sound module using Qt"""

import os

SYSTEM = None

try:
    import gst
    import gobject
    gobject.threads_init()
    SYSTEM = 'gst'
except:
    try:
        from PyQt4.phonon import Phonon
        SYSTEM = 'phonon'
    except Exception, e:
        print e

print "DEBUG::Using %s as sound system" % SYSTEM

class SoundSystem:
    def __init__(self, sounds_path, disable=False):
        self.sounds_path = sounds_path
        self.activate()
        self.disable = disable
        self.sounds = {}

        if SYSTEM == 'gst':
            self.sounds['startup'] = GstSound(os.path.join(self.sounds_path, 'startup.ogg'))
            self.sounds['notification_1'] = GstSound(os.path.join(self.sounds_path, 'notification-1.ogg'))
            self.sounds['notification_2'] = GstSound(os.path.join(self.sounds_path, 'notification-2.ogg'))
        elif SYSTEM == 'phonon':
            self.sounds['startup'] = QtSound(os.path.join(self.sounds_path, 'startup.ogg'))
            self.sounds['notification_1'] = QtSound(os.path.join(self.sounds_path, 'notification-1.ogg'))
            self.sounds['notification_2'] = QtSound(os.path.join(self.sounds_path, 'notification-2.ogg'))
        else:
            self.sounds['startup'] = DummySound()
            self.sounds['notification_1'] = DummySound()
            self.sounds['notification_2'] = DummySound()

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def startup(self):
        self.sounds['startup'].play()

    def notification_1(self):
        self.sounds['notification_1'].play()

    def notification_2(self):
        self.sounds['notification_2'].play()


class GstSound:
    def __init__(self, file_path):
        self.player = gst.element_factory_make("playbin2", "player")
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.__on_gst_message)
        self.player.set_property("uri", "file://" + file_path)

    def __on_gst_message(self, bus, message):
        type_ = message.type
        if type_ == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif type_ == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            err, debug = message.parse_error()

    def play(self):
        self.player.set_state(gst.STATE_PLAYING)


class QtSound:
    def __init__(self, file_path):
        self.sound = Phonon.createPlayer(Phonon.MusicCategory, Phonon.MediaSource(file_path))

    def play(self):
        self.sound.play()

class DummySound:
    def __init__(self):
        pass

    def play(self):
        pass

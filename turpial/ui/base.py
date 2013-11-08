# -*- coding: utf-8 -*-

# Base class for all the Turpial interfaces
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import os
import pdb
import sys
import time
import base64
import urllib
import logging
import webbrowser
import subprocess

from xml.sax.saxutils import unescape

from turpial import VERSION
from turpial.ui.lang import i18n
from turpial.singleton import Singleton

from libturpial.common import OS_MAC
from libturpial.common.tools import detect_os

MIN_WINDOW_WIDTH = 250

class Base(Singleton):
    ACTION_REPEAT = 'repeat'
    ACTION_UNREPEAT = 'unrepeat'
    ACTION_FAVORITE = 'favorite'
    ACTION_UNFAVORITE = 'unfavorite'

    '''Parent class for every UI interface'''
    def __init__(self):
        Singleton.__init__(self, 'turpial.pid')

        self.images_path = os.path.realpath(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'pixmaps'))
        self.sounds_path = os.path.realpath(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'sounds'))
        self.fonts_path = os.path.realpath(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'fonts'))
        self.home_path = os.path.expanduser('~')
        if detect_os() == OS_MAC:
            self.shortcut_key = 'Cmd'
        else:
            self.shortcut_key = 'Ctrl'

        # Unity integration
        #self.unitylauncher = UnityLauncherFactory().create();
        #self.unitylauncher.add_quicklist_button(self.show_update_box, i18n.get('new_tweet'), True)
        #self.unitylauncher.add_quicklist_checkbox(self.sound.disable, i18n.get('enable_sounds'), True, not self.sound._disable)
        #self.unitylauncher.add_quicklist_button(self.show_update_box_for_direct, i18n.get('direct_message'), True)
        #self.unitylauncher.add_quicklist_button(self.show_accounts_dialog, i18n.get('accounts'), True)
        #self.unitylauncher.add_quicklist_button(self.show_preferences, i18n.get('preferences'), True)
        #self.unitylauncher.add_quicklist_button(self.main_quit, i18n.get('exit'), True)
        #self.unitylauncher.show_menu()

    # TODO: Put this in util.py
    def humanize_size(self, size):
        if size == 0:
            return '0 B'

        kbsize = size / 1024
        if kbsize > 0:
            mbsize = kbsize / 1024
            if mbsize > 0:
                gbsize = mbsize / 1024
                if gbsize > 0:
                    return "%.2f GB" % (mbsize / 1024.0)
                else:
                    return "%.2f MB" % (kbsize / 1024.0)
            else:
                return "%.2f KB" % (size / 1024.0)
        else:
            return "%.2f B" % size

    def humanize_timestamp(self, status_timestamp):
        now = time.time()
        # FIXME: Workaround to fix the timestamp
        offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        seconds = now - status_timestamp + offset

        minutes = seconds / 60.0
        if minutes < 1.0:
            timestamp = i18n.get('now')
        else:
            if minutes < 60.0:
                timestamp = "%i m" % minutes
            else:
                hours = minutes / 60.0
                if hours < 24.0:
                    timestamp = "%i h" % hours
                else:
                    dt = time.localtime(status_timestamp)
                    month = time.strftime(u'%b', dt)
                    year = dt.tm_year

                    if year == time.localtime(now).tm_year:
                        timestamp = u"%i %s" % (dt.tm_mday, month)
                    else:
                        timestamp = u"%i %s %i" % (dt.tm_mday, month, year)
        return timestamp

    def get_shortcut_string(self, key):
        return "+".join([self.shortcut_key, key])

    #================================================================
    # Common methods to all interfaces
    #================================================================

    #================================================================
    # Methods to override
    #================================================================

    def main_loop(self):
        raise NotImplementedError

    def main_quit(self, widget=None, force=False):
        raise NotImplementedError

    def show_main(self):
        raise NotImplementedError

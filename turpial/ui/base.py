# -*- coding: utf-8 -*-

# Base class for all the Turpial interfaces
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import os
import time

from turpial.ui.lang import i18n
from turpial.singleton import Singleton

from libturpial.common import OS_MAC
from libturpial.common.tools import detect_os

MIN_WINDOW_WIDTH = 250
BROADCAST_ACCOUNT = 'broadcast'

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
        # Keep a list of installed app fonts to ease registration
        # in the toolkit side
        self.fonts = [
            os.path.join(self.fonts_path, f)
            for f in os.listdir(self.fonts_path)
        ]

        self.home_path = os.path.expanduser('~')

        if detect_os() == OS_MAC:
            self.command_key_shortcut = u'⌘'
            self.command_separator = ''
        else:
            self.command_key_shortcut = 'Ctrl'
            self.command_separator = '+'

        self.bgcolor = "#363636"
        self.fgcolor = "#fff"

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
    def humanize_size(self, size, unit='B', decimals=2):
        if size == 0:
            rtn = '0 %s' % unit
            return rtn.strip()

        prefix = ''
        kbsize = size / 1024
        if kbsize > 0:
            mbsize = kbsize / 1024
            if mbsize > 0:
                gbsize = mbsize / 1024
                if gbsize > 0:
                    prefix = 'G'
                    amount = mbsize / 1024.0
                else:
                    prefix = 'M'
                    amount = kbsize / 1024.0
            else:
                prefix = 'K'
                amount = size / 1024.0
        else:
            amount = size

        if (prefix != ''):
            amount = round(amount, decimals)

        rtn = "%s %s%s" % (amount, prefix, unit)
        return rtn.strip()

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

    def humanize_time_intervals(self, interval):
        if interval > 1:
            unit = i18n.get('minutes')
        else:
            unit = i18n.get('minute')
        return " ".join([str(interval), unit])

    def get_shortcut_string(self, key, modifier=None):
        if modifier:
            return self.command_separator.join([self.command_key_shortcut, modifier, key])
        else:
            return self.command_separator.join([self.command_key_shortcut, key])

    def get_error_message_from_response(self, response, default=None):
        if response is None:
            return default

        if 'errors' in response:
            if 'message' in reponse['errors']:
                msg = response['errors']['message']
                if msg.find('Rate limit exceeded') >= 0:
                    return i18n.get('rate_limit_exceeded')
                elif msg.find('you are not authorized to see') >= 0:
                    return i18n.get('not_authorized_to_see_status')
        return default

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

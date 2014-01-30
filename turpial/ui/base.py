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
            self.shortcut_key = 'Cmd'
        else:
            self.shortcut_key = 'Ctrl'

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

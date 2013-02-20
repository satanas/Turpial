# -*- coding: utf-8 -*-

# Notification module for Turpial """

import os
import logging

from turpial.ui.lang import i18n

log = logging.getLogger('Notify')

NOTIFY = True

try:
    #import pynotify
    #from glib import GError
    NOTIFY = False
except ImportError:
    log.debug("pynotify is not installed")
    NOTIFY = False

class Notification:
    def __init__(self, disable=False):
        self.activate()
        self.disable = disable

        if not NOTIFY:
            log.debug('Module not available')
            self.disable = True
            return

        if disable:
            log.debug('Module disabled')

    def toggle_activation(self):
        if self.active:
            self.active = False
        else:
            self.active = True

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def popup(self, title, message, icon=None):
        if self.disable:
            log.debug('Module disabled. Showing no notifications')
            return

        global NOTIFY
        if self.active and NOTIFY:
            if pynotify.init("Turpial"):
                if not icon:
                    iconpath = os.path.join(os.path.dirname(__file__), 'data',
                        'pixmaps', 'turpial-notification.png')
                    icon = os.path.realpath(iconpath)
                icon = "file://%s" % icon
                notification = pynotify.Notification(title, message, icon)
                try:
                    notification.show()
                except GError:
                    log.debug('Notification service not running')
                    NOTIFY = False

    def updates(self, column, count):
        object_name = ''
        if column.protocol_id == 'twitter':
            if count > 1:
                object_name = i18n.get('new_tweets')
            else:
                object_name = i18n.get('new_tweet')
        else:
            if count > 1:
                object_name = i18n.get('new_dents')
            else:
                object_name = i18n.get('new_dent')
        message = "%s :: %s (%s)" % (column.account_id.split('-')[0],
            column.column_name, i18n.get(column.protocol_id))

        self.popup('%i %s' % (count, object_name), message)

    def login(self, profile):
        object_name = ''
        if profile.get_protocol_id() == 'twitter':
            if profile.statuses_count > 1:
                object_name = i18n.get('tweets')
            else:
                object_name = i18n.get('tweet')
        else:
            if profile.statuses_count > 1:
                object_name = i18n.get('dents')
            else:
                object_name = i18n.get('dent')

        self.popup('@%s' % profile.username,
            '%s: %i\n%s: %i\n%s: %i' %
            (object_name, profile.statuses_count,
            i18n.get('following'), profile.friends_count,
            i18n.get('followers'), profile.followers_count))

    def following(self, user, follow):
        name = user.username
        if follow:
            self.popup(i18n.get('turpial_follow'), i18n.get('you_are_now_following') % name)
        else:
            self.popup(i18n.get('turpial_unfollow'), i18n.get('you_are_no_longer_following') % name)

    def following_error(self, message, follow):
        if follow:
            self.popup(i18n.get('turpial_follow'), message)
        else:
            self.popup(i18n.get('turpial_unfollow'), message)

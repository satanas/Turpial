# -*- coding: utf-8 -*-

# Notification module for Turpial

import os
import logging

from turpial.ui.lang import i18n
from libturpial.common import get_username_from

NOTIFY = True

try:
    import pynotify
except ImportError:
    NOTIFY = False

class OSNotificationSystem:
    def __init__(self, images_path, disable=False):
        self.images_path = images_path
        self.activate()
        self.disable = disable

        if not NOTIFY:
            self.disable = True
            return

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def notify(self, title, message, icon=None):
        if self.disable:
            return

        if self.active and not self.disable:
            if pynotify.init("Turpial"):
                if not icon:
                    iconpath = os.path.join(self.images_path, 'turpial-notification.png')
                    icon = os.path.realpath(iconpath)
                icon = "file://%s" % icon
                notification = pynotify.Notification(title, message, icon)
                try:
                    notification.show()
                except Exception, e:
                    print e

    def updates(self, column, count, filtered=0):
        if count > 1:
            message = i18n.get('new_tweets') % count
        elif count == 1:
            message = i18n.get('new_tweet')
        else:
            message = i18n.get('no_new_tweets')

        filtered_message = ''
        if filtered == 1:
            filtered_message = ''.join([' (', i18n.get('tweet_filtered'), ')'])
        elif filtered > 1:
            filtered_message = ''.join([' (', i18n.get('tweets_filtered') % filtered, ')'])

        message += filtered_message

        title = "%s-%s %s" % (get_username_from(column.account_id),
                              column.slug, i18n.get('has_been_updated'))
        self.notify(title, message)

    def user_followed(self, username):
        self.notify(i18n.get('follow'), i18n.get('you_are_now_following') % username)

    def user_unfollowed(self, username):
        self.notify(i18n.get('unfollow'), i18n.get('you_are_no_longer_following') % username)

    def user_reported_as_spam(self, username):
        self.notify(i18n.get('report_as_spam'), i18n.get('has_been_reported_as_spam') % username)

    def user_blocked(self, username):
        self.notify(i18n.get('block'), i18n.get('has_been_blocked') % username)

    def user_muted(self, username):
        self.notify(i18n.get('mute'), i18n.get('has_been_muted') % username)

    def user_unmuted(self, username):
        self.notify(i18n.get('unmute'), i18n.get('has_been_unmuted') % username)

    def message_enqueued_successfully(self):
        self.notify(i18n.get('message_enqueued'), i18n.get('message_enqueued_successfully'))

    def message_from_queue_posted(self):
        self.notify(i18n.get('message_updated'), i18n.get('message_from_queue_has_been_posted'))

    def message_from_queue_broadcasted(self):
        self.notify(i18n.get('message_broadcasted'),
                    i18n.get('message_from_queue_has_been_broadcasted'))

    def message_enqueued_due_error(self):
        self.notify(i18n.get('message_enqueued'), i18n.get('message_enqueued_due_error'))

    def following_error(self, message, follow):
        if follow:
            self.popup(i18n.get('turpial_follow'), message)
        else:
            self.popup(i18n.get('turpial_unfollow'), message)

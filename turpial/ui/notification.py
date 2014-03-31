# -*- coding: utf-8 -*-

# Notification module for Turpial

import os
import logging

from turpial.ui.lang import i18n
from libturpial.common import OS_LINUX, OS_MAC
from libturpial.common.tools import get_username_from, detect_os

LINUX_NOTIFY = True
OSX_NOTIFY = True

try:
    import pynotify
except ImportError:
    LINUX_NOTIFY = False

try:
    from Foundation import NSUserNotification
    from Foundation import NSUserNotificationCenter
except ImportError:
    OSX_NOTIFY = False

class NotificationSystem:
    @staticmethod
    def create(images_path):
        current_os = detect_os()
        if current_os == OS_LINUX:
            return LinuxNotificationSystem(images_path)
        elif current_os == OS_MAC:
            return OsxNotificationSystem(images_path)

class BaseNotification:
    def __init__(self, disable=False):
        self.activate()
        self.disable = disable

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def notify(self, title, message, icon=None):
        raise NotImplementedError

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

    def message_queued_successfully(self):
        self.notify(i18n.get('message_queued'), i18n.get('message_queued_successfully'))

    def message_from_queue_posted(self):
        self.notify(i18n.get('message_posted'), i18n.get('message_from_queue_has_been_posted'))

    def message_from_queue_broadcasted(self):
        self.notify(i18n.get('message_broadcasted'),
                    i18n.get('message_from_queue_has_been_broadcasted'))

    def message_queued_due_error(self):
        self.notify(i18n.get('message_queued'), i18n.get('message_queued_due_error'))

    def following_error(self, message, follow):
        if follow:
            self.notify(i18n.get('turpial_follow'), message)
        else:
            self.notify(i18n.get('turpial_unfollow'), message)

class LinuxNotificationSystem(BaseNotification):
    def __init__(self, images_path, disable=False):
        BaseNotification.__init__(self, not LINUX_NOTIFY)
        self.images_path = images_path

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

class OsxNotificationSystem(BaseNotification):
    def __init__(self, images_path, disable=False):
        BaseNotification.__init__(self, not OSX_NOTIFY)
        self.images_path = images_path

    def notify(self, title, message, icon=None):
        if self.disable:
            return

        if self.active and not self.disable:
            notification = NSUserNotification.alloc().init()
            notification.setTitle_(title)
            notification.setInformativeText_(message)

            center = NSUserNotificationCenter.defaultUserNotificationCenter()
            center.scheduleNotification_(notification)
            #center.deliverNotification_(notification)

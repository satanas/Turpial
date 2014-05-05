# -*- coding: utf-8 -*-

# Qt main view for Turpial

import os
import sys
import random
import urllib2
import webbrowser
import subprocess


from functools import partial

from PyQt4.QtGui import (
    QMenu, QImage, QWidget, QAction, QPixmap, QDialog, QMessageBox,
    QVBoxLayout, QApplication, QFontDatabase, QIcon, QDesktopWidget,
)

from PyQt4.QtCore import QTimer, pyqtSignal, QRect, Qt

from turpial.ui.base import * #NOQA
from turpial.ui.sound import SoundSystem
from turpial.ui.notification import NotificationSystem

from turpial.ui.qt.dock import Dock
from turpial.ui.qt.tray import TrayIcon
from turpial.ui.qt.worker import CoreWorker
from turpial.ui.qt.queue import QueueDialog
from turpial.ui.qt.about import AboutDialog
from turpial.ui.qt.search import SearchDialog
from turpial.ui.qt.shortcuts import Shortcuts
from turpial.ui.qt.updatebox import UpdateBox
from turpial.ui.qt.container import Container
from turpial.ui.qt.imageview import ImageView
from turpial.ui.qt.filters import FiltersDialog
from turpial.ui.qt.profile import ProfileDialog
from turpial.ui.qt.accounts import AccountsDialog
from turpial.ui.qt.preferences import PreferencesDialog
from turpial.ui.qt.selectfriend import SelectFriendDialog

from libturpial.common import ColumnType, get_preview_service_from_url, escape_list_name, OS_MAC
from libturpial.common.tools import detect_os


# Exceptions
#{u'errors': [{u'message': u'Sorry, you are not authorized to see this status.', u'code': 179}]}
#Exception 'id'

class Main(Base, QWidget):

    account_deleted = pyqtSignal()
    account_loaded = pyqtSignal()
    account_registered = pyqtSignal()

    def __init__(self, debug=False):
        self.app = QApplication(['Turpial'] + sys.argv)

        Base.__init__(self)
        QWidget.__init__(self)

        self.debug = debug

        for font_path in self.fonts:
            QFontDatabase.addApplicationFont(font_path)

        #database = QFontDatabase()
        #for f in database.families():
        #    print f

        self.templates_path = os.path.realpath(os.path.join(
            os.path.dirname(__file__), 'templates'))

        self.setWindowTitle('Turpial')
        self.app.setApplicationName('Turpial')
        self.setWindowIcon(QIcon(self.get_image_path('turpial.svg')))
        self.resize(320, 480)
        self.center_on_screen()

        self.ignore_quit = True
        self.showed = True
        self.core_ready = False
        self.timers = {}
        self.extra_friends = []

        self.update_box = UpdateBox(self)
        self.profile_dialog = ProfileDialog(self)
        self.profile_dialog.options_clicked.connect(self.show_profile_menu)
        self.image_view = ImageView(self)
        self.queue_dialog = QueueDialog(self)
        self.shortcuts = Shortcuts(self)

        self.core = CoreWorker()
        self.core.ready.connect(self.after_core_initialized)
        self.core.status_updated.connect(self.after_update_status)
        self.core.status_broadcasted.connect(self.after_broadcast_status)
        self.core.status_repeated.connect(self.after_repeat_status)
        self.core.status_deleted.connect(self.after_delete_status)
        self.core.message_deleted.connect(self.after_delete_message)
        self.core.message_sent.connect(self.after_send_message)
        self.core.column_updated.connect(self.after_update_column)
        self.core.account_saved.connect(self.after_save_account)
        self.core.account_loaded.connect(self.after_load_account)
        self.core.account_deleted.connect(self.after_delete_account)
        self.core.column_saved.connect(self.after_save_column)
        self.core.column_deleted.connect(self.after_delete_column)
        self.core.status_marked_as_favorite.connect(self.after_marking_status_as_favorite)
        self.core.status_unmarked_as_favorite.connect(self.after_unmarking_status_as_favorite)
        self.core.fetched_user_profile.connect(self.after_get_user_profile)
        self.core.urls_shorted.connect(self.update_box.after_short_url)
        self.core.media_uploaded.connect(self.update_box.after_upload_media)
        self.core.friends_list_updated.connect(self.update_box.update_friends_list)
        self.core.user_muted.connect(self.after_mute_user)
        self.core.user_unmuted.connect(self.after_unmute_user)
        self.core.user_blocked.connect(self.after_block_user)
        self.core.user_reported_as_spam.connect(self.after_report_user_as_spam)
        self.core.user_followed.connect(self.after_follow_user)
        self.core.user_unfollowed.connect(self.after_unfollow_user)
        self.core.status_from_conversation.connect(self.after_get_status_from_conversation)
        self.core.fetched_profile_image.connect(self.after_get_profile_image)
        self.core.fetched_avatar.connect(self.update_profile_avatar)
        self.core.fetched_image_preview.connect(self.after_get_image_preview)
        self.core.status_pushed_to_queue.connect(self.after_push_status_to_queue)
        self.core.status_poped_from_queue.connect(self.after_pop_status_from_queue)
        self.core.status_posted_from_queue.connect(self.after_post_status_from_queue)
        self.core.status_deleted_from_queue.connect(self.after_delete_status_from_queue)
        self.core.queue_cleared.connect(self.after_clear_queue)
        self.core.exception_raised.connect(self.on_exception)

        self.core.start()

        self._container = Container(self)

        self.os_notifications = NotificationSystem.create(self.images_path)
        self.sounds = SoundSystem(self.sounds_path)

        self.dock = Dock(self)

        self.dock.accounts_clicked.connect(self.show_accounts_dialog)
        self.dock.columns_clicked.connect(self.show_column_menu)
        self.dock.search_clicked.connect(self.show_search_dialog)
        self.dock.updates_clicked.connect(self.show_update_box)
        self.dock.messages_clicked.connect(self.show_friends_dialog_for_direct_message)
        self.dock.queue_clicked.connect(self.show_queue_dialog)
        self.dock.filters_clicked.connect(self.show_filters_dialog)
        self.dock.preferences_clicked.connect(self.show_preferences_dialog)
        self.dock.quit_clicked.connect(self.main_quit)

        self.tray = TrayIcon(self)
        self.tray.toggled.connect(self.toggle_tray_icon)
        self.tray.updates_clicked.connect(self.show_update_box)
        self.tray.messages_clicked.connect(self.show_friends_dialog_for_direct_message)
        self.tray.settings_clicked.connect(self.show_preferences_dialog)
        self.tray.quit_clicked.connect(self.main_quit)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._container, 1)
        layout.addWidget(self.dock)

        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.add_keyboard_shortcuts()

    def open_in_browser(self, url):
        browser = self.core.get_default_browser()

        if browser != '':
            cmd = browser.split(' ')
            cmd.append(url)
            subprocess.Popen(cmd)
        else:
            webbrowser.open(url)

    def toggle_tray_icon(self):
        if self.showed:
            if self.isActiveWindow():
                self.showed = False
                self.hide()
            else:
                self.raise_()
        else:
            self.showed = True
            self.show()
            self.raise_()

    def add_keyboard_shortcuts(self):
        for key, shortcut in self.shortcuts:
            if detect_os() != OS_MAC and key == 'preferences':
                continue
            self.addAction(shortcut.action)

        self.shortcuts.get('accounts').activated.connect(self.show_accounts_dialog)
        self.shortcuts.get('filters').activated.connect(self.show_filters_dialog)
        self.shortcuts.get('tweet').activated.connect(self.show_update_box)
        self.shortcuts.get('message').activated.connect(self.show_friends_dialog_for_direct_message)
        self.shortcuts.get('search').activated.connect(self.show_search_dialog)
        self.shortcuts.get('queue').activated.connect(self.show_queue_dialog)
        self.shortcuts.get('quit').activated.connect(self.closeEvent)

        if detect_os() == OS_MAC:
            self.shortcuts.get('preferences').activated.connect(self.show_preferences_dialog)

    def add_extra_friends_from_statuses(self, statuses):
        current_friends_list = self.load_friends_list()
        for status in statuses:
            for user in status.get_mentions():
                if user not in current_friends_list and user not in self.extra_friends:
                    self.extra_friends.append(user)

    def is_exception(self, response):
        return isinstance(response, Exception)

    def random_id(self):
        return str(random.getrandbits(128))

    def center_on_screen(self):
        current_position = self.frameGeometry()
        current_position.moveCenter(self.app.desktop().availableGeometry().center())
        self.move(current_position.topLeft())

    def get_screen_size(self):
        return self.app.desktop().availableGeometry()

    def resizeEvent(self, event):
        if self.core.status > self.core.LOADING:
            self.core.set_window_size(event.size().width(), event.size().height())

    def closeEvent(self, event=None):
        if event:
            event.ignore()

        if self.core.status > self.core.LOADING:
            if self.core.get_minimize_on_close():
                self.hide()
                self.showed = False
            else:
                self.main_quit()
        else:
            confirmation = self.show_confirmation_message(i18n.get('confirm_close'),
                i18n.get('do_you_want_to_close_turpial'))
            if confirmation:
                self.main_quit()

    #================================================================
    # Overrided methods
    #================================================================

    def start(self):
        pass

    def restart(self):
        self.core.restart()
        self._container.loading()

    def main_loop(self):
        try:
            self.app.exec_()
        except Exception:
            sys.exit(0)

    def main_quit(self, widget=None, force=False):
        self.app.quit()
        sys.exit(0)

    def show_main(self):
        self.start()
        self.show()

    #================================================================
    # Main methods
    #================================================================

    def show_error_message(self, title, message, error):
        full_message = "%s (%s)" % (message, error)
        message = QMessageBox.critical(self, title, full_message, QMessageBox.Ok)

    def show_information_message(self, title, message):
        message = QMessageBox.information(self, title, message, QMessageBox.Ok)

    def show_confirmation_message(self, title, message):
        confirmation = QMessageBox.question(self, title, message,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmation == QMessageBox.No:
            return False
        return True

    def show_about_dialog(self):
        AboutDialog(self)

    def show_accounts_dialog(self):
        accounts = AccountsDialog(self)

    def show_queue_dialog(self):
        self.queue_dialog.show()

    def show_profile_dialog(self, account_id, username):
        self.profile_dialog.start_loading(username)
        self.core.get_user_profile(account_id, username)

    def show_preferences_dialog(self):
        self.preferences_dialog = PreferencesDialog(self)

    def show_search_dialog(self):
        search = SearchDialog(self)
        if search.result() == QDialog.Accepted:
            account_id = str(search.get_account().toPyObject())
            criteria = str(search.get_criteria())
            self.add_search_column(account_id, criteria)

    def show_filters_dialog(self):
        self.filters_dialog = FiltersDialog(self)

    def show_profile_image(self, account_id, username):
        self.image_view.start_loading()
        self.core.get_profile_image(account_id, username)

    def show_update_box(self):
        self.update_box.show()

    def show_update_box_for_reply(self, account_id, status):
        self.update_box.show_for_reply(account_id, status)

    def show_update_box_for_quote(self, account_id, status):
        self.update_box.show_for_quote(account_id, status)

    def show_update_box_for_send_direct(self, account_id, username):
        self.update_box.show_for_send_direct(account_id, username)

    def show_update_box_for_reply_direct(self, account_id, status):
        self.update_box.show_for_reply_direct(account_id, status)

    def show_column_menu(self, point):
        self.columns_menu = self.build_columns_menu()
        self.columns_menu.exec_(point)

    def show_profile_menu(self, point, profile):
        self.profile_menu = QMenu(self)


        if profile.following:
            message_menu = QAction(i18n.get('send_direct_message'), self)
            message_menu.triggered.connect(partial(
                self.show_update_box_for_send_direct, profile.account_id, profile.username))
            self.profile_menu.addAction(message_menu)

        if self.core.is_muted(profile.username):
            mute_menu = QAction(i18n.get('unmute'), self)
            mute_menu.triggered.connect(partial(self.unmute, profile.username))
        else:
            mute_menu = QAction(i18n.get('mute'), self)
            mute_menu.triggered.connect(partial(self.mute, profile.username))

        block_menu = QAction(i18n.get('block'), self)
        block_menu.triggered.connect(partial(self.block, profile.account_id, profile.username))
        spam_menu = QAction(i18n.get('report_as_spam'), self)
        spam_menu.triggered.connect(partial(self.report_as_spam, profile.account_id,
            profile.username))

        # FIXME: Use the profile_url variable in libturpial's twitter.py
        # Put this value on every profile object
        user_profile_url = "http://twitter.com/%s" % (profile.username)
        open_in_browser_menu = QAction(i18n.get('open_in_browser'), self)
        open_in_browser_menu.triggered.connect(lambda x: self.open_in_browser(user_profile_url))

        self.profile_menu.addAction(open_in_browser_menu)
        self.profile_menu.addAction(mute_menu)
        self.profile_menu.addAction(block_menu)
        self.profile_menu.addAction(spam_menu)

        self.profile_menu.exec_(point)

    def show_friends_dialog_for_direct_message(self):
        friend = SelectFriendDialog(self)
        if friend.is_accepted():
            self.show_update_box_for_send_direct(friend.get_account(), friend.get_username())

    def save_account(self, account):
        self.core.save_account(account)

    def load_account(self, account_id):
        self.core.load_account(account_id)

    def delete_account(self, account_id):
        self.core.delete_account(account_id)

    def add_column(self, column_id):
        self.core.save_column(column_id)

    def add_search_column(self, account_id, criteria):
        column_id = "%s-%s>%s" % (account_id, ColumnType.SEARCH, urllib2.quote(criteria))
        self.add_column(column_id)

    def get_column_from_id(self, column_id):
        columns = self.core.get_registered_columns()
        for column in columns:
            if column_id == column.id_:
                return column
        return None

    def get_shorten_url_service(self):
        return self.core.get_shorten_url_service()

    def get_upload_media_service(self):
        return self.core.get_upload_media_service()

    def load_friends_list(self):
        return self.core.load_friends_list()

    def load_friends_list_with_extras(self):
        return self.extra_friends + self.core.load_friends_list()

    def open_url(self, url):
        preview_service = get_preview_service_from_url(url)
        if preview_service and not self.core.get_show_images_in_browser():
            self.core.get_image_preview(preview_service, url)
            self.image_view.start_loading(image_url=url)
        else:
            self.open_in_browser(url)

    def load_image(self, filename, pixbuf=False):
        img_path = os.path.join(self.images_path, filename)
        if pixbuf:
            return QPixmap(img_path)
        return QImage(img_path)

    def get_image_path(self, filename):
        return os.path.join(self.images_path, filename)

    def update_dock(self):
        accounts = self.core.get_registered_accounts()
        columns = self.core.get_registered_columns()

        if len(columns) == 0:
            if len(accounts) == 0:
                self.dock.empty(False)
            else:
                self.dock.normal()
        else:
            self.dock.normal()

    def update_container(self):
        accounts = self.core.get_registered_accounts()
        columns = self.core.get_registered_columns()

        if len(columns) == 0:
            if len(accounts) == 0:
                self._container.empty(False)
                self.dock.empty(False)
            else:
                self._container.empty(True)
                self.dock.normal()
            self.tray.empty()
        else:
            self._container.normal()
            self.dock.normal()
            self.tray.normal()
            for column in columns:
                self.download_stream(column)
                self.add_timer(column)
            self.fetch_friends_list()

    def build_columns_menu(self):
        columns_menu = QMenu(self)

        available_columns = self.core.get_available_columns()
        accounts = self.core.get_all_accounts()

        if len(accounts) == 0:
            empty_menu = QAction(i18n.get('no_registered_accounts'), self)
            empty_menu.setEnabled(False)
            columns_menu.addAction(empty_menu)
        else:
            for account in accounts:
                name = "%s (%s)" % (account.username, i18n.get(account.protocol_id))
                account_menu = QAction(name, self)

                if len(available_columns[account.id_]) > 0:
                    available_columns_menu = QMenu(self)
                    for column in available_columns[account.id_]:
                        item = QAction(column.slug, self)
                        if column.__class__.__name__ == 'List':
                            slug = escape_list_name(column.slug)
                            column_id = "-".join([account.id_, slug])
                            item.triggered.connect(partial(self.add_column, column_id))
                        else:
                            item.triggered.connect(partial(self.add_column, column.id_))
                        available_columns_menu.addAction(item)

                    account_menu.setMenu(available_columns_menu)
                else:
                    account_menu.setEnabled(False)
                columns_menu.addAction(account_menu)

        return columns_menu

    def update_status(self, account_id, message, in_reply_to_id=None):
        self.core.update_status(account_id, message, in_reply_to_id)

    def update_status_with_media(self, account_id, message, in_reply_to_id=None, media=None):
        self.core.update_status_with_media(account_id, message, in_reply_to_id, media)

    def broadcast_status(self, message):
        accounts = []
        for account in self.core.get_registered_accounts():
            accounts.append(account.id_)
        self.core.broadcast_status(accounts, message)

    def repeat_status(self, column_id, account_id, status):
        self.core.repeat_status(column_id, account_id, status.id_)

    def delete_status(self, column_id, account_id, status):
        self.core.delete_status(column_id, account_id, status.id_)

    def delete_direct_message(self, column_id, account_id, status):
        self.core.delete_direct_message(column_id, account_id, status.id_)

    def send_direct_message(self, account_id, username, message):
        self.core.send_direct_message(account_id, username, message)

    def mark_status_as_favorite(self, column_id, account_id, status):
        self.core.mark_status_as_favorite(column_id, account_id, status.id_)

    def unmark_status_as_favorite(self, column_id, account_id, status):
        self.core.unmark_status_as_favorite(column_id, account_id, status.id_)

    def short_urls(self, message):
        self.core.short_urls(message)

    def upload_media(self, account_id, filename):
        self.core.upload_media(account_id, filename)

    def fetch_friends_list(self):
        self.core.get_friends_list()

    def mute(self, username):
        self.core.mute(username)

    def unmute(self, username):
        self.core.unmute(username)

    def block(self, account_id, username):
        self.core.block(account_id, username)

    def report_as_spam(self, account_id, username):
        self.core.report_as_spam(account_id, username)

    def follow(self, account_id, username):
        self.core.follow(account_id, username)

    def unfollow(self, account_id, username):
        self.core.unfollow(account_id, username)

    def get_conversation(self, account_id, status, column_id, status_root_id):
        self.core.get_status_from_conversation(account_id, status.in_reply_to_id, column_id,
            status_root_id)

    def push_status_to_queue(self, account_id, message):
        self.core.push_status_to_queue(account_id, message)

    def update_status_from_queue(self, args=None):
        self.core.pop_status_from_queue()

    def delete_message_from_queue(self, index):
        self.core.delete_status_from_queue(index)

    def clear_queue(self):
        self.core.clear_statuses_queue()

    def get_config(self):
        return self.core.read_config()

    def get_cache_size(self):
        return self.humanize_size(self.core.get_cache_size())

    def clean_cache(self):
        self.core.delete_cache()

    def save_filters(self, filters):
        self.core.save_filters(filters)

    def update_config(self, new_config):
        current_config = self.core.read_config()
        current_queue_interval = int(current_config['General']['queue-interval'])

        self.core.update_config(new_config)

        if current_queue_interval != new_config['General']['queue-interval']:
            self.turn_on_queue_timer(force=True)

    def restore_config(self):
        self.core.restore_config()

    def set_column_update_interval(self, column_id, interval):
        self.core.set_update_interval_per_column(column_id, interval)

    def get_column_update_interval(self, column_id):
        return self.core.get_update_interval_per_column(column_id)

    def set_column_notification(self, column_id, value):
        self.core.set_show_notifications_in_column(column_id, value)

    def get_column_notification(self, column_id):
        return self.core.get_show_notifications_in_column(column_id)

    #================================================================
    # Hooks definitions
    #================================================================

    def after_core_initialized(self, response):
        if self.is_exception(response):
            self.core.status = self.core.ERROR
            self._container.error()
        else:
            self.core.add_config_option('General', 'minimize-on-close', 'off')
            self.core.add_config_option('General', 'inline-preview', 'off')
            self.core.add_config_option('General', 'show-images-in-browser', 'off')
            self.core.add_config_option('General', 'queue-interval', 30)
            self.core.add_config_option('Window', 'size', '320,480')
            self.core.add_config_option('Notifications', 'actions', 'on')
            self.core.add_config_option('Notifications', 'updates', 'on')
            self.core.add_config_option('Sounds', 'updates', 'on')
            self.core.add_config_option('Sounds', 'login', 'on')
            self.core.add_config_option('Browser', 'cmd', '')
            self.core.add_config_option('Advanced', 'show-user-avatars', 'on')

            # This is for backwards compatibility
            columns = self.core.sanitize_search_columns()
            notifications = self.core.read_section('Notifications')
            updates = self.core.read_section('Updates')

            if updates is None:
                updates = {}

            for key in columns:
                if key not in notifications.keys():
                    notifications[key] = 'on' if self.core.get_notify_on_updates() else 'off'
                if key not in updates.keys():
                    updates[key] = self.core.get_update_interval()

            self.core.write_section('Notifications', notifications)
            self.core.write_section('Updates', updates)

            # Remove deprecated config values
            self.core.remove_config_option('Notifications', 'on-updates')
            self.core.remove_config_option('Notifications', 'on-actions')
            self.core.remove_config_option('Sounds', 'on-updates')
            self.core.remove_config_option('Sounds', 'on-actions')
            self.core.remove_config_option('Sounds', 'on-login')

            width, height = self.core.get_window_size()
            self.resize(width, height)
            self.center_on_screen()
            if self.core.get_sound_on_login():
                self.sounds.startup()
            self.queue_dialog.start()
            self.update_container()
            self.turn_on_queue_timer()
            self.core.status = self.core.READY

    def after_save_account(self, account_id):
        self.account_registered.emit()
        if len(self.core.get_registered_accounts()) == 1:
            self.update_container()
        self.update_dock()
        timeline = "%s-timeline" % account_id
        self.add_column(timeline)

    def after_load_account(self):
        self.account_loaded.emit()

    def after_delete_account(self):
        self.account_deleted.emit()

    def after_delete_column(self, column_id):
        column_id = str(column_id)
        self._container.remove_column(column_id)
        self.remove_timer(column_id)

        columns = self.core.get_registered_columns()
        if len(columns) == 0:
            self.update_container()

    def after_save_column(self, column_id):
        column_id = str(column_id)
        self._container.add_column(column_id)
        column = self.get_column_from_id(column_id)
        self.download_stream(column)
        self.add_timer(column)

    def after_update_column(self, response, data):
        column, max_ = data

        if self.is_exception(response):
            print 'Ble', response
            self._container.error_updating_column(column.id_)
        else:
            count = len(response)
            if count > 0:
                updates = self.core.filter_statuses(response)
                filtered = count - len(updates)
                if self.core.get_show_notifications_in_column(column.id_):
                    self.os_notifications.updates(column, len(updates), filtered)

                if self.core.get_sound_on_updates():
                    self.sounds.updates()
                self._container.update_column(column.id_, updates)
            else:
                self._container.update_timestamps(column.id_)


    def after_update_status(self, response, account_id):
        if self.is_exception(response):
            self.update_box.error(i18n.get('error_posting_status'))
        else:
            self.update_box.done()

    def after_broadcast_status(self, response):
        if self.is_exception(response):
            self.update_box.error(i18n.get('error_posting_status'))
        else:
            self.update_box.done()

    def after_repeat_status(self, response, column_id, account_id, status_id):
        column_id = str(column_id)
        if self.is_exception(response):
            if self.profile_dialog.is_for_profile(column_id):
                self.profile_dialog.error_repeating_status(status_id)
            else:
                self._container.error_repeating_status(column_id, status_id)
        else:
            message = i18n.get('status_repeated')
            self._container.mark_status_as_repeated(response.id_)

            if self.profile_dialog.is_for_profile(column_id):
                self.profile_dialog.last_statuses.mark_status_as_repeated(response.id_)
                self.profile_dialog.last_statuses.release_status(response.id_)
                self.profile_dialog.last_statuses.notify_success(response.id_, message)
            else:
                self._container.notify_success(column_id, response.id_, message)

    def after_delete_status(self, response, column_id, account_id, status_id):
        if self.is_exception(response):
            self._container.error_deleting_status(column_id, status_id)
        else:
            self._container.remove_status(response.id_)
            self._container.notify_success(column_id, response.id_, i18n.get('status_deleted'))

    def after_delete_message(self, response, column_id, account_id, status_id):
        if self.is_exception(response):
            self._container.error_deleting_status(column_id, status_id)
        else:
            self._container.remove_status(response.id_)
            self._container.notify_success(column_id, response.id_, i18n.get('direct_message_deleted'))

    def after_send_message(self, response, account_id):
        if self.is_exception(response):
            self.update_box.error(i18n.get('can_not_send_direct_message'))
        else:
            self.update_box.done()

    def after_marking_status_as_favorite(self, response, column_id, account_id, status_id):
        column_id = str(column_id)
        if self.is_exception(response):
            if self.profile_dialog.is_for_profile(column_id):
                self.profile_dialog.error_marking_status_as_favorite(status_id)
            else:
                self._container.error_marking_status_as_favorite(column_id, status_id)
        else:
            message = i18n.get('status_marked_as_favorite')
            self._container.mark_status_as_favorite(response.id_)

            if self.profile_dialog.is_for_profile(column_id):
                self.profile_dialog.last_statuses.mark_status_as_favorite(response.id_)
                self.profile_dialog.last_statuses.release_status(response.id_)
                self.profile_dialog.last_statuses.notify_success(response.id_, message)
            else:
                self._container.notify_success(column_id, response.id_, message)

    def after_unmarking_status_as_favorite(self, response, column_id, account_id, status_id):
        column_id = str(column_id)
        if self.is_exception(response):
            if self.profile_dialog.is_for_profile(column_id):
                self.profile_dialog.error_unmarking_status_as_favorite(status_id)
            else:
                self._container.error_unmarking_status_as_favorite(column_id, status_id)
        else:
            message = i18n.get('status_removed_from_favorites')
            self._container.unmark_status_as_favorite(response.id_)

            if self.profile_dialog.is_for_profile(column_id):
                self.profile_dialog.last_statuses.unmark_status_as_favorite(response.id_)
                self.profile_dialog.last_statuses.release_status(response.id_)
                self.profile_dialog.last_statuses.notify_success(response.id_, message)
            else:
                self._container.notify_success(column_id, response.id_, message)

    def after_get_user_profile(self, response, account_id):
        if self.is_exception(response):
            self.profile_dialog.error(i18n.get('problems_loading_user_profile'))
        else:
            self.profile_dialog.loading_finished(response, account_id)
            self.core.get_avatar_from_status(response)

    def after_mute_user(self, username):
        if self.core.get_notify_on_actions():
            self.os_notifications.user_muted(username)

    def after_unmute_user(self, username):
        if self.core.get_notify_on_actions():
            self.os_notifications.user_unmuted(username)

    def after_block_user(self, profile):
        if self.is_exception(profile):
            self.profile_dialog.error(i18n.get('could_not_block_user'))
        else:
            if self.core.get_notify_on_actions():
                self.os_notifications.user_blocked(profile.username)

    def after_report_user_as_spam(self, profile):
        if self.is_exception(profile):
            self.profile_dialog.error(i18n.get('having_issues_reporting_user_as_spam'))
        else:
            if self.core.get_notify_on_actions():
                self.os_notifications.user_reported_as_spam(profile.username)

    def after_follow_user(self, profile):
        if self.is_exception(profile):
            self.profile_dialog.error(i18n.get('having_trouble_to_follow_user'))
        else:
            self.profile_dialog.update_following(profile.username, True)
            if self.core.get_notify_on_actions():
                self.os_notifications.user_followed(profile.username)

    def after_unfollow_user(self, profile):
        if self.is_exception(profile):
            self.profile_dialog.error(i18n.get('having_trouble_to_unfollow_user'))
        else:
            self.profile_dialog.update_following(profile.username, False)
            if self.core.get_notify_on_actions():
                self.os_notifications.user_unfollowed(profile.username)

    def after_get_status_from_conversation(self, response, column_id, status_root_id):
        column_id = str(column_id)
        if self.is_exception(response):
            if self.profile_dialog.is_for_profile(column_id):
                self.profile_dialog.error_loading_conversation(status_root_id)
            else:
                self._container.error_loading_conversation(column_id, status_root_id)
        else:
            if self.profile_dialog.is_for_profile(column_id):
                self.profile_dialog.last_statuses.update_conversation(response, status_root_id)
            else:
                self._container.update_conversation(response, column_id, status_root_id)

            if response.in_reply_to_id:
                self.core.get_status_from_conversation(response.account_id, response.in_reply_to_id,
                    column_id, status_root_id)

    def after_get_profile_image(self, image_path):
        self.image_view.load_from_url(str(image_path))

    def update_profile_avatar(self, image_path, username):
        if not self.is_exception(image_path):
            self.profile_dialog.update_avatar(str(image_path), str(username))

    def after_get_image_preview(self, response):
        if self.is_exception(response):
            self.image_view.error()
        else:
            self.image_view.load_from_object(response)

    def after_push_status_to_queue(self, account_id):
        self.update_box.done()
        self.turn_on_queue_timer()
        if self.core.get_notify_on_actions():
            self.os_notifications.message_queued_successfully()

    def after_pop_status_from_queue(self, status):
        if status:
            self.core.post_status_from_queue(status.account_id, status.text)

    def after_post_status_from_queue(self, response, account_id, message):
        if self.is_exception(response):
            if self.core.get_notify_on_actions():
                self.os_notifications.message_queued_due_error()
            print "+++Message queued again for error posting"
            self.push_status_to_queue(account_id, message)
        else:
            self.turn_off_queue_timer()
            if self.core.get_notify_on_actions():
                if account_id == BROADCAST_ACCOUNT:
                    self.os_notifications.message_from_queue_broadcasted()
                else:
                    self.os_notifications.message_from_queue_posted()

    def after_delete_status_from_queue(self):
        self.queue_dialog.update()

    def after_clear_queue(self):
        self.queue_dialog.update()
        self.queue_dialog.update_timestamp()
        self.turn_off_queue_timer()

    def on_exception(self, exception):
        print 'Exception', exception

    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------

    def add_timer(self, column):
        self.remove_timer(column.id_)

        interval = self.core.get_update_interval_per_column(column.id_) * 60 * 1000
        timer = Timer(interval, column, self.download_stream)
        self.timers[column.id_] = timer
        print '--Created timer for %s every %i sec' % (column.id_, interval)

    def remove_timer(self, column_id):
        if column_id in self.timers:
            self.timers[column_id].stop()
            del self.timers[column_id]
            print '--Removed timer for %s' % column_id

    def download_stream(self, column):
        if self._container.is_updating(column.id_):
            return True

        last_id = self._container.start_updating(column.id_)
        self.core.get_column_statuses(column, last_id)
        return True

    def set_queue_timer(self):
        self.remove_timer('queue')
        interval = self.core.get_queue_interval() * 60 * 1000
        timer = Timer(interval, None, self.update_status_from_queue)
        self.timers['queue'] = timer
        print '--Created timer for queue every %i sec' % interval

    def turn_on_queue_timer(self, force=False):
        self.queue_dialog.update()
        if (len(self.core.list_statuses_queue()) > 0 and 'queue' not in self.timers) or force:
            self.set_queue_timer()
            self.queue_dialog.update_timestamp()

    def turn_off_queue_timer(self):
        self.queue_dialog.update()
        if len(self.core.list_statuses_queue()) == 0:
            self.remove_timer('queue')
            self.queue_dialog.update_timestamp()

class Timer:
    def __init__(self, interval, column, callback):
        self.interval = interval
        self.column = column
        self.callback = callback
        self.timer = QTimer()
        self.timer.timeout.connect(self.__on_timeout)
        self.timer.start(interval)

    def __on_timeout(self):
        self.callback(self.column)

    def get_id(self):
        return self.timer.timerId()

    def stop(self):
        self.timer.stop()

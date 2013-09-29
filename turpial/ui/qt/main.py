# -*- coding: utf-8 -*-

# Qt main view for Turpial

import os
import sys
import urllib2
import traceback

from functools import partial

from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QImage
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QFontDatabase
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QApplication

from PyQt4.QtCore import QTimer
from PyQt4.QtCore import pyqtSignal

from turpial import DESC
from turpial.ui.base import *

from turpial.ui.qt.dock import Dock
from turpial.ui.qt.tray import TrayIcon
from turpial.ui.qt.worker import CoreWorker
from turpial.ui.qt.search import SearchDialog
from turpial.ui.qt.updatebox import UpdateBox
from turpial.ui.qt.container import Container
from turpial.ui.qt.profile import ProfileDialog
from turpial.ui.qt.accounts import AccountsDialog
from turpial.ui.qt.selectfriend import SelectFriendDialog
from turpial.ui.qt.imageview import ImageView

from libturpial.common import ColumnType, is_preview_service_supported

class Main(Base, QWidget):

    account_deleted = pyqtSignal()
    account_registered = pyqtSignal()

    def __init__(self):
        self.app = QApplication(sys.argv)

        Base.__init__(self)
        QWidget.__init__(self)

        QFontDatabase.addApplicationFont(os.path.join(self.fonts_path, 'Ubuntu-L.ttf'))
        QFontDatabase.addApplicationFont(os.path.join(self.fonts_path, 'TitilliumWeb-Bold.ttf'))
        QFontDatabase.addApplicationFont(os.path.join(self.fonts_path, 'TitilliumWeb-Regular.ttf'))
        QFontDatabase.addApplicationFont(os.path.join(self.fonts_path, 'Monda-Regular.ttf'))

        database = QFontDatabase()
        for f in database.families():
            print f

        self.templates_path = os.path.realpath(os.path.join(
            os.path.dirname(__file__), 'templates'))

        self.setWindowTitle('Turpial')
        self.ignore_quit = True
        self.resize(320, 480)
        self.showed = True
        self.timers = {}

        self.update_box = UpdateBox(self)
        self.profile = ProfileDialog(self)
        self.profile.options_clicked.connect(self.show_profile_menu)

        self.core = CoreWorker()
        self.core.status_updated.connect(self.after_update_status)
        self.core.status_broadcasted.connect(self.after_broadcast_status)
        self.core.status_repeated.connect(self.after_repeat_status)
        self.core.status_deleted.connect(self.after_delete_status)
        self.core.message_deleted.connect(self.after_delete_message)
        self.core.message_sent.connect(self.after_send_message)
        self.core.column_updated.connect(self.after_update_column)
        self.core.account_saved.connect(self.after_save_account)
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
        self.core.exception_raised.connect(self.on_exception)

        self.core.start()

        self._container = Container(self)

        self.dock = Dock(self)
        self.dock.empty()

        self.dock.accounts_clicked.connect(self.show_accounts_dialog)
        self.dock.columns_clicked.connect(self.show_column_menu)
        self.dock.search_clicked.connect(self.show_search_dialog)
        self.dock.updates_clicked.connect(self.show_update_box)
        self.dock.messages_clicked.connect(self.show_friends_dialog_for_direct_message)

        self.tray = TrayIcon(self)
        self.tray.toggled.connect(self.toggle_tray_icon)
        self.tray.updates_clicked.connect(self.show_update_box)
        self.tray.messages_clicked.connect(self.show_friends_dialog_for_direct_message)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._container, 1)
        layout.addWidget(self.dock)
        layout.setMargin(0)

        self.setLayout(layout)

        self.image_view = ImageView(self)

    def __open_in_browser(self, url):
        browser = self.core.get_default_browser()

        if browser != '':
            cmd = browser.split(' ')
            cmd.append(url)
            subprocess.Popen(cmd)
        else:
            webbrowser.open(url)


    def toggle_tray_icon(self):
        if self.showed:
            self.showed = False
            self.hide()
        else:
            self.showed = True
            self.show()

    #================================================================
    # Overrided methods
    #================================================================

    def start(self):
        #if self.core.play_sounds_in_login():
        #    self.sound.login()
        print 'start'

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
        self.update_container()

    #================================================================
    # Main methods
    #================================================================

    def save_account(self, account):
        self.core.save_account(account)

    def delete_account(self, account_id):
        self.core.delete_account(account_id)

    def add_column(self, column_id):
        self.core.save_column(column_id)

    def add_search_column(self, account_id, criteria):
        column_id = "%s-%s:%s" % (account_id, ColumnType.SEARCH, urllib2.quote(criteria))
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

    def open_url(self, url):
        if is_preview_service_supported(url):
            self.__open_in_browser(url)
            pass
            #try:
            #    bla
            #except:
            #    self.__open_in_browser(url)
        else:
            self.__open_in_browser(url)

    def load_image(self, filename, pixbuf=False):
        img_path = os.path.join(self.images_path, filename)
        if pixbuf:
            return QPixmap(img_path)
        return QImage(img_path)

    def get_image_path(self, filename):
        return os.path.join(self.images_path, filename)

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
            self.get_friend_list()

    def show_accounts_dialog(self):
        accounts = AccountsDialog(self)

    def show_column_menu(self, point):
        self.columns_menu = QMenu(self)

        available_columns = self.core.get_available_columns()
        accounts = self.core.get_all_accounts()

        if len(accounts) == 0:
            empty_menu = QAction(i18n.get('no_registered_accounts'), self)
            empty_menu.setEnabled(False)
            self.columns_menu.addAction(empty_menu)
        else:
            for account in accounts:
                name = "%s (%s)" % (account.username, i18n.get(account.protocol_id))
                account_menu = QAction(name, self)

                if len(available_columns[account.id_]) > 0:
                    available_columns_menu = QMenu(self)
                    for column in available_columns[account.id_]:
                        # FIXME: Handle lists
                        if column.__class__.__name__ == 'List':
                            continue
                        item = QAction(column.slug, self)
                        item.triggered.connect(partial(self.add_column, column.id_))
                        available_columns_menu.addAction(item)

                    account_menu.setMenu(available_columns_menu)
                else:
                    account_menu.setEnabled(False)
                self.columns_menu.addAction(account_menu)

        self.columns_menu.exec_(point)

    def show_search_dialog(self):
        search = SearchDialog(self)
        if search.result() == QDialog.Accepted:
            account_id = str(search.get_account().toPyObject())
            criteria = str(search.get_criteria())
            self.add_search_column(account_id, criteria)

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

    def show_profile_dialog(self, account_id, profile):
        self.profile.start_loading(profile)
        self.core.get_user_profile(account_id, profile)

    def show_profile_menu(self, point, profile):
        self.profile_menu = QMenu(self)

        if profile.following:
            unfollow_menu = QAction(i18n.get('unfollow'), self)
            unfollow_menu.triggered.connect(partial(self.unfollow, profile.account_id,
                profile.username))
            message_menu = QAction(i18n.get('send_direct_message'), self)
            message_menu.triggered.connect(partial(
                self.show_update_box_for_send_direct, profile.account_id, profile.username))
            self.profile_menu.addAction(unfollow_menu)
            self.profile_menu.addSeparator()
            self.profile_menu.addAction(message_menu)
        elif profile.follow_request:
            follow_menu = QAction(i18n.get('follow_requested'), self)
            follow_menu.setEnabled(False)
            self.profile_menu.addAction(follow_menu)
            self.profile_menu.addSeparator()
        else:
            follow_menu = QAction(i18n.get('follow'), self)
            follow_menu.triggered.connect(partial(self.follow, profile.account_id,
                profile.username))
            self.profile_menu.addAction(follow_menu)
            self.profile_menu.addSeparator()

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

        self.profile_menu.addAction(mute_menu)
        self.profile_menu.addAction(block_menu)
        self.profile_menu.addAction(spam_menu)

        self.profile_menu.exec_(point)

    def show_friends_dialog_for_direct_message(self):
        friend = SelectFriendDialog(self)
        if friend.get_username():
            self.show_update_box_for_send_direct(friend.get_account(), friend.get_username())

    def update_status(self, account_id, message, in_reply_to_id=None):
        self.core.update_status(account_id, message, in_reply_to_id)

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

    def get_friend_list(self):
        self.core.get_friend_list()

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

    def show_profile_image(self, account_id, username):
        self.image_view.start_loading()
        self.core.get_profile_image(account_id, username)


    #================================================================
    # Hooks definitions
    #================================================================

    def after_save_account(self):
        self.account_registered.emit()

    def after_delete_account(self):
        self.account_deleted.emit()

    def after_delete_column(self, column_id):
        column_id = str(column_id)
        self._container.remove_column(column_id)
        self.remove_timer(column_id)

    def after_save_column(self, column_id):
        column_id = str(column_id)
        self._container.add_column(column_id)
        column = self.get_column_from_id(column_id)
        self.download_stream(column)
        self.add_timer(column)

    def after_update_column(self, arg, data):
        column, max_ = data

        # Notifications
        # FIXME
        count = len(arg)

        if count > 0:
            self._container.update_column(column.id_, arg)

    def after_update_status(self, response, account_id):
        self.update_box.done()

    def after_broadcast_status(self, response):
        self.update_box.done()

    def after_repeat_status(self, response, column_id, account_id):
        self._container.mark_status_as_repeated(response.id_)
        self._container.notify_success(str(column_id), response.id_, i18n.get('status_repeated'))

    def after_delete_status(self, response, column_id, account_id):
        self._container.remove_status(response.id_)
        self._container.notify_success(str(column_id), response.id_, i18n.get('status_deleted'))

    def after_delete_message(self, response, column_id, account_id):
        self._container.remove_status(response.id_)
        self._container.notify_success(str(column_id), response.id_, i18n.get('direct_message_deleted'))

    def after_send_message(self, response, account_id):
        self.update_box.done()

    def after_marking_status_as_favorite(self, response, column_id, account_id):
        self._container.mark_status_as_favorite(response.id_)
        self._container.notify_success(str(column_id), response.id_,
            i18n.get('status_marked_as_favorite'))


    def after_unmarking_status_as_favorite(self, response, column_id, account_id):
        self._container.unmark_status_as_favorite(response.id_)
        self._container.notify_success(str(column_id), response.id_,
            i18n.get('status_removed_from_favorites'))

    def after_get_user_profile(self, response, account_id):
        self.profile.loading_finished(response, account_id)

    def after_mute_user(self, response):
        print "User %s muted" % response

    def after_unmute_user(self, response):
        print "User %s unmuted" % response

    def after_block_user(self, response):
        print "User %s blocked" % response.username

    def after_report_user_as_spam(self, response):
        print "User %s reported" % response.username

    def after_follow_user(self, response):
        print "User %s followed" % response.username

    def after_unfollow_user(self, response):
        print "User %s unfollowed" % response.username

    def after_get_status_from_conversation(self, response, column_id, status_root_id):
        self._container.update_conversation(response, column_id, status_root_id)
        if response.in_reply_to_id:
            self.core.get_status_from_conversation(response.account_id, response.in_reply_to_id,
                column_id, status_root_id)

    def after_get_profile_image(self, image_path):
        self.image_view.loading_finished(str(image_path))

    def on_exception(self, exception):
        print 'Exception', exception

    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------

    def add_timer(self, column):
        self.remove_timer(column.id_)

        interval = self.core.get_update_interval() * 60 * 1000
        timer = Timer(interval, column, self.download_stream)
        self.timers[column.id_] = timer
        print '--Created timer for %s every %i sec' % (column.id_, interval)

    def remove_timer(self, column_id):
        if self.timers.has_key(column_id):
            self.timers[column_id].stop()
            del self.timers[column_id]
            print '--Removed timer for %s' % column_id

    def download_stream(self, column):
        print 'updating %s' % column
        if self._container.is_updating(column.id_):
            return True

        last_id = self._container.start_updating(column.id_)
        self.core.get_column_statuses(column, last_id)
        return True

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

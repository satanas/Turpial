# -*- coding: utf-8 -*-

# Qt Worker for Turpial

import os
import Queue

from PyQt4.QtCore import QThread
from PyQt4.QtCore import pyqtSignal

from libturpial.api.core import Core
from libturpial.api.models.status import Status
from libturpial.api.models.column import Column
from libturpial.common.tools import get_account_id_from, get_column_slug_from

class CoreWorker(QThread):

    ready = pyqtSignal(object)
    status_updated = pyqtSignal(object, str)
    status_broadcasted = pyqtSignal(object)
    status_repeated = pyqtSignal(object, str, str, str)
    status_deleted = pyqtSignal(object, str, str, str)
    status_pushed_to_queue = pyqtSignal(str)
    status_poped_from_queue = pyqtSignal(object)
    status_deleted_from_queue = pyqtSignal()
    queue_cleared = pyqtSignal()
    status_posted_from_queue = pyqtSignal(object, str, str)
    message_deleted = pyqtSignal(object, str, str)
    message_sent = pyqtSignal(object, str)
    column_updated = pyqtSignal(object, tuple)
    account_saved = pyqtSignal()
    account_loaded = pyqtSignal()
    account_deleted = pyqtSignal()
    column_saved = pyqtSignal(str)
    column_deleted = pyqtSignal(str)
    status_marked_as_favorite = pyqtSignal(object, str, str, str)
    status_unmarked_as_favorite = pyqtSignal(object, str, str, str)
    fetched_user_profile = pyqtSignal(object, str)
    urls_shorted = pyqtSignal(object)
    media_uploaded = pyqtSignal(object)
    friends_list_updated = pyqtSignal()
    user_muted = pyqtSignal(str)
    user_unmuted = pyqtSignal(str)
    user_blocked = pyqtSignal(object)
    user_reported_as_spam = pyqtSignal(object)
    user_followed = pyqtSignal(object, str)
    user_unfollowed = pyqtSignal(object, str)
    exception_raised = pyqtSignal(object)
    status_from_conversation = pyqtSignal(object, str, str)
    fetched_profile_image = pyqtSignal(object)
    fetched_avatar = pyqtSignal(object, str)
    fetched_image_preview = pyqtSignal(object)
    cache_deleted = pyqtSignal()

    ERROR = -1
    LOADING = 0
    READY = 1

    def __init__(self):
        QThread.__init__(self)
        self.queue = Queue.Queue()
        self.exit_ = False
        self.status = self.LOADING
        #self.core = Core()

        #self.queue_path = os.path.join(self.core.config.basedir, 'queue')
        #if not os.path.isfile(self.queue_path):
        #    open(self.queue_path, 'w').close()
        self.core = None
        self.restart()

    #def __del__(self):
    #    self.wait()

    def restart(self):
        self.register(self.login, (), self.__after_login, None)

    def __get_from_queue(self, index=0):
        lines = open(self.queue_path).readlines()
        if not lines:
            return None

        row = lines[index].strip()
        account_id, message = row.split("\1")
        del lines[index]

        open(self.queue_path, 'w').writelines(lines)
        status = Status()
        status.account_id = account_id
        status.text = message
        return status

    def __get_column_num_from_id(self, column_id):
        column_key = None
        for i in range(1, len(self.get_registered_columns()) + 1):
            column_num = "column%s" % i
            stored_id = self.core.config.read('Columns', column_num)
            if stored_id == column_id:
                column_key = column_num
            else:
                i += 1
        return column_key

    #================================================================
    # Core methods
    #================================================================

    def login(self):
        self.core = Core()
        self.queue_path = os.path.join(self.core.config.basedir, 'queue')
        if not os.path.isfile(self.queue_path):
            open(self.queue_path, 'w').close()

    def get_default_browser(self):
        return self.core.get_default_browser()

    def get_update_interval(self):
        return self.core.get_update_interval()

    def get_statuses_per_column(self):
        return self.core.get_max_statuses_per_column()

    def get_minimize_on_close(self):
        return self.core.minimize_on_close()

    # FIXME: Implement support on libturpial
    def get_proxy_configuration(self):
        return self.core.config.read_section('Proxy')

    # FIXME: Implement support on libturpial
    def get_socket_timeout(self):
        return int(self.core.config.read('Advanced', 'socket-timeout'))

    def get_show_user_avatars(self):
        show_avatars = self.core.config.read('Advanced', 'show-user-avatars')
        return True if show_avatars == 'on' else False

    def get_update_interval_per_column(self, column_id):
        column_key = self.__get_column_num_from_id(column_id)

        key = "%s-update-interval" % column_key
        interval = self.core.config.read('Intervals', key)
        if not interval:
            # FIXME: Fix in libturpial
            config = self.core.config.read_all()
            if not config.has_key('Intervals'):
                config['Intervals'] = {key: 5}
                self.core.config.save(config)
            else:
                self.core.config.write('Intervals', key, 5)
            config = self.core.config.read_all()
            interval = "5"
        return int(interval)

    def set_update_interval_in_column(self, column_id, interval):
        column_key = self.__get_column_num_from_id(column_id)

        key = "%s-update-interval" % column_key
        self.core.config.write('Intervals', key, interval)
        return interval

    def get_show_notifications_in_column(self, column_id):
        column_key = self.__get_column_num_from_id(column_id)

        key = "%s-notifications" % column_key
        notifications = self.core.config.read('Notifications', key)
        if not notifications:
            # FIXME: Fix in libturpial
            config = self.core.config.read_all()
            if not config.has_key('Notifications'):
                config['Notifications'] = {}
                self.core.config.save(config)
            self.core.config.write('Notifications', key, 'on')
            notifications = 'on'

        if notifications == 'on':
            return True
        return False

    def set_show_notifications_in_column(self, column_id, value):
        column_key = self.__get_column_num_from_id(column_id)

        key = "%s-notifications" % column_key
        if value:
            notifications = 'on'
        else:
            notifications = 'off'
        self.core.config.write('Notifications', key, notifications)
        return value

    def get_cache_size(self):
        return self.core.get_cache_size()

    def delete_cache(self):
        self.core.delete_cache()

    def get_sound_on_login(self):
        sound_on_login = self.core.config.read('Sounds', 'login')
        if sound_on_login is None:
            self.core.config.write('Sounds', 'login', 'on')
            return True
        else:
            if sound_on_login == 'on':
                return True
            return False

    def get_sound_on_updates(self):
        sound_on_update = self.core.config.read('Sounds', 'updates')
        if sound_on_update is None:
            self.core.config.write('Sounds', 'updates', 'on')
            return True
        else:
            if sound_on_update == 'on':
                return True
            return False

    def get_notify_on_updates(self):
        try:
            notify_on_update = self.core.config.cfg.get('Notifications', 'updates', raw=True)
            if notify_on_update == 'on':
                return True
            return False
        except:
            config = self.read_config()
            config['Notifications']['on-updates'] = 'on'
            self.core.save_all_config(config)
            return True

    def get_notify_on_actions(self):
        try:
            notify_on_actions = self.core.config.cfg.get('Notifications', 'actions', raw=True)
            if notify_on_actions == 'on':
                return True
            return False
        except:
            config = self.read_config()
            config['Notifications']['actions'] = 'on'
            self.core.save_all_config(config)
            return True

    def get_queue_interval(self):
        try:
            queue_interval = self.core.config.cfg.get('General', 'queue-interval', raw=True)
            return int(queue_interval)
        except:
            config = self.read_config()
            config['General']['queue-interval'] = 30
            self.core.save_all_config(config)
            return config['General']['queue-interval']

    def read_config(self):
        config = {}

        # FIXME: Implemen this on libturpial
        for section in self.core.config.cfg.sections():
            if not config.has_key(section):
                config[section] = {}

            for item in self.core.config.cfg.items(section, raw=True):
                for value in item:
                    config[section][item[0]] = item[1]
        return config

    def update_config(self, new_config):
        self.core.save_all_config(new_config)

    def get_shorten_url_service(self):
        return self.core.get_shorten_url_service()

    def get_upload_media_service(self):
        return self.core.get_upload_media_service()

    def get_available_columns(self):
        return self.core.available_columns()

    def get_all_accounts(self):
        return self.core.registered_accounts()

    def get_all_columns(self):
        return self.core.all_columns()

    def get_registered_accounts(self):
        return self.core.registered_accounts()

    def get_available_short_url_services(self):
        return self.core.available_short_url_services()

    def get_available_upload_media_services(self):
        return self.core.available_upload_media_services()

    def get_registered_columns(self):
        i = 1
        columns = []
        while True:
            column_num = "column%s" % i
            column_id = self.core.config.read('Columns', column_num)
            if column_id:
                account_id = get_account_id_from(column_id)
                column_slug = get_column_slug_from(column_id)
                columns.append(Column(account_id, column_slug))
                i += 1
            else:
                break
        return columns

    def is_muted(self, username):
        return self.core.is_muted(username)

    def load_friends_list(self):
        return self.core.load_all_friends_list()

    def save_account(self, account):
        account_id = self.core.register_account(account)
        self.__after_save_account()

    # FIXME: Remove this after implement this in libturpial
    def load_account(self, account_id, trigger_signal=True):
        if trigger_signal:
            self.register(self.core.account_manager.load, (account_id),
                self.__after_load_account)
        else:
            self.core.account_manager.load(account_id)
            self.__after_load_account()

    def delete_account(self, account_id):
        # FIXME: Implement try/except
        for col in self.get_registered_columns():
            if col.account_id == account_id:
                self.delete_column(col.id_)
        self.core.unregister_account(str(account_id), True)
        self.__after_delete_account()

    def save_column(self, column_id):
        #FIXME: Hack to avoid the libturpial error saving config
        self.update_config(self.read_config())
        reg_column_id = self.core.register_column(column_id)
        self.__after_save_column(reg_column_id)

    def delete_column(self, column_id):
        deleted_column = self.core.unregister_column(column_id)
        self.__after_delete_column(column_id)

    def get_column_statuses(self, column, last_id):
        count = self.core.get_max_statuses_per_column()
        self.register(self.core.get_column_statuses, (column.account_id,
            column.slug, count, last_id), self.__after_update_column,
            (column, count))

    def update_status(self, account_id, message, in_reply_to_id=None):
        self.register(self.core.update_status, (account_id,
            message, in_reply_to_id), self.__after_update_status, account_id)

    def broadcast_status(self, accounts, message):
        self.register(self.core.broadcast_status, (accounts, message),
            self.__after_broadcast_status)

    def repeat_status(self, column_id, account_id, status_id):
        self.register(self.core.repeat_status, (account_id, status_id),
            self.__after_repeat_status, (column_id, account_id, status_id))

    def delete_status(self, column_id, account_id, status_id):
        self.register(self.core.destroy_status, (account_id, status_id),
            self.__after_delete_status, (column_id, account_id, status_id))

    def delete_direct_message(self, column_id, account_id, status_id):
        self.register(self.core.destroy_direct_message, (account_id, status_id),
            self.__after_delete_direct_message, (column_id, account_id))

    def send_direct_message(self, account_id, username, message):
        self.register(self.core.send_direct_message, (account_id, username,
            message), self.__after_send_direct_message, account_id)

    def mark_status_as_favorite(self, column_id, account_id, status_id):
        self.register(self.core.mark_status_as_favorite, (account_id, status_id),
            self.__after_mark_status_as_favorite, (column_id, account_id, status_id))

    def unmark_status_as_favorite(self, column_id, account_id, status_id):
        self.register(self.core.unmark_status_as_favorite, (account_id, status_id),
            self.__after_unmark_status_as_favorite, (column_id, account_id, status_id))

    def get_user_profile(self, account_id, user_profile=None):
        self.register(self.core.get_user_profile, (account_id, user_profile),
            self.__after_get_user_profile, account_id)

    def short_urls(self, message):
        self.register(self.core.short_url_in_message, (message),
            self.__after_short_urls)

    def upload_media(self, account_id, filepath):
        self.register(self.core.upload_media, (account_id, filepath),
            self.__after_upload_media)

    def get_friends_list(self):
        self.register(self.core.get_all_friends_list, None,
            self.__after_get_friends_list)

    def mute(self, username):
        self.register(self.core.mute, username, self.__after_mute_user)

    def unmute(self, username):
        self.register(self.core.unmute, username, self.__after_unmute_user)

    def block(self, account_id, username):
        self.register(self.core.block, (account_id, username), self.__after_block_user)

    def report_as_spam(self, account_id, username):
        self.register(self.core.report_as_spam, (account_id, username),
            self.__after_report_user_as_spam)

    def follow(self, account_id, username):
        self.register(self.core.follow, (account_id, username),
            self.__after_follow_user, account_id)

    def unfollow(self, account_id, username):
        self.register(self.core.unfollow, (account_id, username),
            self.__after_unfollow_user, account_id)

    def get_status_from_conversation(self, account_id, status_id, column_id, status_root_id):
        self.register(self.core.get_single_status, (account_id, status_id),
            self.__after_get_status_from_conversation, (column_id, status_root_id))

    def get_profile_image(self, account_id, username):
        self.register(self.core.get_profile_image, (account_id, username),
            self.__after_get_profile_image)

    def get_avatar_from_status(self, status):
        self.register(self.core.get_status_avatar, (status),
            self.__after_get_avatar_from_status, status.username)

    def get_image_preview(self, preview_service, url):
        self.register(preview_service.do_service, (url),
            self.__after_get_image_preview)

    def push_status_to_queue(self, account_id, message):
        fd = open(self.queue_path, 'a+')
        row = "%s\1%s\n" % (account_id, message)
        fd.write(row.encode('utf-8'))
        fd.close()
        self.__after_push_status_to_queue(account_id)

    def pop_status_from_queue(self):
        status = self.__get_from_queue()
        self.__after_pop_status_from_queue(status)

    def delete_status_from_queue(self, index=0):
        status = self.__get_from_queue(index)
        self.__after_delete_status_from_queue()

    def list_statuses_queue(self):
        statuses = []
        lines = []
        if os.path.exists(self.queue_path):
            lines = open(self.queue_path).readlines()
        for line in lines:
            account_id, message = line.strip().split("\1")
            status = Status()
            status.account_id = account_id
            status.text = message
            statuses.append(status)
        return statuses

    def clear_statuses_queue(self):
        open(self.queue_path, 'w').writelines([])
        self.__after_clear_queue()

    def post_status_from_queue(self, account_id, message):
        self.register(self.core.update_status, (account_id, message),
            self.__after_post_status_from_queue, (account_id, message))

    def delete_cache(self):
        self.register(self.core.delete_cache, None, self.__after_delete_cache)

    def list_filters(self):
        return self.core.list_filters()

    def save_filters(self, filters):
        self.core.save_filters(filters)

    def restore_config(self):
        self.core.delete_current_config()

    def get_window_size(self):
        try:
            size = self.core.config.cfg.get('Window', 'size', raw=True)
            window_size = int(size.split(',')[0]), int(size.split(',')[1])
            return window_size
        except:
            config = self.read_config()
            config['Window']['size'] = "320,480"
            self.core.save_all_config(config)
            return config['Window']['size']

    def set_window_size(self, width, height):
        window_size = "%s,%s" % (width, height)
        #FIXME: Hack to avoid the libturpial error saving config
        self.update_config(self.read_config())
        self.core.config.write('Window', 'size', window_size)

    #================================================================
    # Callbacks
    #================================================================

    def __after_login(self, response):
        self.ready.emit(response)

    def __after_save_account(self):
        self.account_saved.emit()

    def __after_load_account(self, response=None):
        self.account_loaded.emit()

    def __after_delete_account(self):
        self.account_deleted.emit()

    def __after_save_column(self, column_id):
        self.column_saved.emit(column_id)

    def __after_delete_column(self, column_id):
        self.column_deleted.emit(column_id)

    def __after_update_column(self, response, data):
        self.column_updated.emit(response, data)

    def __after_update_status(self, response, account_id):
        self.status_updated.emit(response, account_id)

    def __after_broadcast_status(self, response):
        self.status_broadcasted.emit(response)

    def __after_repeat_status(self, response, args):
        column_id = args[0]
        account_id = args[1]
        status_id = args[2]
        self.status_repeated.emit(response, column_id, account_id, status_id)

    def __after_delete_status(self, response, args):
        column_id = args[0]
        account_id = args[1]
        status_id = args[2]
        self.status_deleted.emit(response, column_id, account_id, status_id)

    def __after_delete_direct_message(self, response, args):
        column_id = args[0]
        account_id = args[1]
        self.message_deleted.emit(response, column_id, account_id)

    def __after_send_direct_message(self, response, account_id):
        self.message_sent.emit(response, account_id)

    def __after_mark_status_as_favorite(self, response, args):
        column_id = args[0]
        account_id = args[1]
        status_id = args[2]
        self.status_marked_as_favorite.emit(response, column_id, account_id, status_id)

    def __after_unmark_status_as_favorite(self, response, args):
        column_id = args[0]
        account_id = args[1]
        status_id = args[2]
        self.status_unmarked_as_favorite.emit(response, column_id, account_id, status_id)

    def __after_get_user_profile(self, response, account_id):
        self.fetched_user_profile.emit(response, account_id)

    def __after_short_urls(self, response):
        self.urls_shorted.emit(response)

    def __after_upload_media(self, response):
        self.media_uploaded.emit(response)

    def __after_get_friends_list(self, response):
        self.friends_list_updated.emit()

    def __after_mute_user(self, response):
        self.user_muted.emit(response)

    def __after_unmute_user(self, response):
        self.user_unmuted.emit(response)

    def __after_block_user(self, response):
        self.user_blocked.emit(response)

    def __after_report_user_as_spam(self, response):
        self.user_reported_as_spam.emit(response)

    def __after_follow_user(self, response, account_id):
        self.user_followed.emit(response, account_id)

    def __after_unfollow_user(self, response, account_id):
        self.user_unfollowed.emit(response, account_id)

    def __after_get_status_from_conversation(self, response, args):
        column_id = args[0]
        status_root_id = args[1]
        self.status_from_conversation.emit(response, column_id, status_root_id)

    def __after_get_profile_image(self, response):
        self.fetched_profile_image.emit(response)

    def __after_get_avatar_from_status(self, response, args):
        username = args
        self.fetched_avatar.emit(response, username)

    def __after_get_image_preview(self, response):
        self.fetched_image_preview.emit(response)

    def __after_push_status_to_queue(self, account_id):
        self.status_pushed_to_queue.emit(account_id)

    def __after_pop_status_from_queue(self, status):
        self.status_poped_from_queue.emit(status)

    def __after_delete_status_from_queue(self):
        self.status_deleted_from_queue.emit()

    def __after_clear_queue(self):
        self.queue_cleared.emit()

    def __after_post_status_from_queue(self, response, args):
        account_id = args[0]
        message = args[1]
        self.status_posted_from_queue.emit(response, account_id, message)

    def __after_delete_cache(self):
        self.cache_deleted.emit()

    #================================================================
    # Worker methods
    #================================================================

    def register(self, funct, args, callback, user_data=None):
        self.queue.put((funct, args, callback, user_data))

    def quit(self):
        self.exit_ = True

    def run(self):
        while not self.exit_:
            try:
                req = self.queue.get(True, 0.3)
            except Queue.Empty:
                continue
            except:
                continue

            (funct, args, callback, user_data) = req

            try:
                if type(args) == tuple:
                    rtn = funct(*args)
                elif args:
                    rtn = funct(args)
                else:
                    rtn = funct()
            except Exception, e:
                #self.exception_raised.emit(e)
                #continue
                rtn = e

            if callback:
                if user_data:
                    callback(rtn, user_data)
                else:
                    callback(rtn)



# -*- coding: utf-8 -*-

# Qt Worker for Turpial

import Queue

from PyQt4.QtCore import QThread
from PyQt4.QtCore import pyqtSignal

from libturpial.api.core import Core
from libturpial.api.models.column import Column
from libturpial.common.tools import get_account_id_from, get_column_slug_from

class CoreWorker(QThread):

    status_updated = pyqtSignal(object, str)
    status_repeated = pyqtSignal(object, str)
    status_deleted = pyqtSignal(object, str)
    column_updated = pyqtSignal(object, tuple)
    account_saved = pyqtSignal()
    account_deleted = pyqtSignal()
    column_saved = pyqtSignal(str)
    column_deleted = pyqtSignal(str)
    status_marked_as_favorite = pyqtSignal(object, str)
    status_unmarked_as_favorite = pyqtSignal(object, str)
    got_user_profile = pyqtSignal(object, str)
    urls_shorted = pyqtSignal(str)
    media_uploaded = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self.queue = Queue.Queue()
        self.exit_ = False
        self.core = Core()

    #def __del__(self):
    #    self.wait()

    #================================================================
    # Core methods
    #================================================================

    def get_default_browser(self):
        return self.core.get_default_browser()

    def get_update_interval(self):
        return self.core.get_update_interval()

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

    def save_account(self, account):
        account_id = self.core.register_account(account)
        self.__after_save_account()

    def delete_account(self, account_id):
        # FIXME: Implement try/except
        for col in self.get_registered_columns():
            if col.account_id == account_id:
                self.delete_column(col.id_)
        self.core.unregister_account(str(account_id), True)
        self.__after_delete_account()

    def save_column(self, column_id):
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

    def repeat_status(self, account_id, status_id):
        self.register(self.core.repeat_status, (account_id, status_id),
            self.__after_repeat_status, account_id)

    def delete_status(self, account_id, status_id):
        self.register(self.core.destroy_status, (account_id, status_id),
            self.__after_delete_status, account_id)

    def mark_status_as_favorite(self, account_id, status_id):
        self.register(self.core.mark_status_as_favorite, (account_id, status_id),
            self.__after_mark_status_as_favorite, account_id)

    def unmark_status_as_favorite(self, account_id, status_id):
        self.register(self.core.unmark_status_as_favorite, (account_id, status_id),
            self.__after_unmark_status_as_favorite, account_id)

    def get_user_profile(self, account_id, user_profile=None):
        self.register(self.core.get_user_profile, (account_id, user_profile),
            self.__after_get_user_profile, account_id)

    def short_urls(self, message):
        self.register(self.core.short_url_in_message, (message),
            self.__after_short_urls)

    def upload_media(self, account_id, filepath):
        self.register(self.core.upload_media, (account_id, filepath),
            self.__after_upload_media)


    #================================================================
    # Callbacks
    #================================================================

    def __after_save_account(self):
        self.account_saved.emit()

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

    def __after_repeat_status(self, response, account_id):
        self.status_repeated.emit(response, account_id)

    def __after_delete_status(self, response, account_id):
        self.status_deleted.emit(response, account_id)

    def __after_mark_status_as_favorite(self, response, account_id):
        self.status_marked_as_favorite.emit(response, account_id)

    def __after_unmark_status_as_favorite(self, response, account_id):
        self.status_unmarked_as_favorite.emit(response, account_id)

    def __after_get_user_profile(self, response, account_id):
        self.got_user_profile.emit(response, account_id)

    def __after_short_urls(self, response):
        self.urls_shorted.emit(response)

    def __after_upload_media(self, response):
        self.media_uploaded.emit(response)

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

            if type(args) == tuple:
                rtn = funct(*args)
            elif args:
                rtn = funct(args)
            else:
                rtn = funct()

            if callback:
                if user_data:
                    callback(rtn, user_data)
                else:
                    callback(rtn)



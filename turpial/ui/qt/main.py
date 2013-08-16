# -*- coding: utf-8 -*-

# Qt main view for Turpial

import os
import sys
import urllib2

from functools import partial

from PyQt4 import QtCore
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QImage
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QFontDatabase
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QApplication

from PyQt4.QtCore import pyqtSignal

from turpial import DESC
from turpial.ui.base import *

from turpial.ui.qt.dock import Dock
from turpial.ui.qt.worker import Worker
from turpial.ui.qt.tray import TrayIcon
from turpial.ui.qt.update import UpdateBox
from turpial.ui.qt.search import SearchDialog
from turpial.ui.qt.container import Container
from turpial.ui.qt.profile import ProfileDialog
from turpial.ui.qt.accounts import AccountsDialog
from turpial.ui.qt.selectfriend import SelectFriendDialog

from libturpial.api.core import Core
from libturpial.common import ColumnType
from libturpial.api.models.column import Column
from libturpial.common.tools import get_account_id_from, get_column_slug_from

class Main(Base, QWidget):

    account_deleted = pyqtSignal()
    account_registered = pyqtSignal()

    def __init__(self, core):
        self.app = QApplication(sys.argv)

        Base.__init__(self, core)
        QWidget.__init__(self)
        QFontDatabase.addApplicationFont('/home/satanas/proyectos/turpial2/turpial/data/fonts/RopaSans-Regular.ttf')
        QFontDatabase.addApplicationFont('/home/satanas/proyectos/turpial2/turpial/data/fonts/Monda-Regular.ttf')
        path = os.path.join(os.path.dirname(__file__), '../../data/fonts/Cicle_Gordita.ttf')
        id_ = QFontDatabase.addApplicationFont(path)
        path = os.path.join(os.path.dirname(__file__), '../../data/fonts/Aaargh.ttf.ttf')
        id_ = QFontDatabase.addApplicationFont(path)
        #QFontDatabase.addApplicationFont('/home/satanas/proyectos/turpial2/turpial/data/fonts/RopaSans-Regular.ttf')
        #QFontDatabase.addApplicationFont('/home/satanas/proyectos/turpial2/turpial/data/fonts/Monda-Regular.ttf')

        self.setWindowTitle('Turpial')
        self.ignore_quit = True
        self.resize(320, 480)
        self.showed = True

        self.tray = TrayIcon(self)
        self.tray.activated.connect(self.__on_tray_click)

        self.core = Core()

        self.worker = Worker()
        self.worker.start()

        #self.worker.register(self.core.list_accounts, None, self.__test)

        self._container = Container(self)
        #self._container.empty()

        self.dock = Dock(self)
        self.dock.empty()

        self.dock.accounts_clicked.connect(self.show_accounts_dialog)
        self.dock.columns_clicked.connect(self.show_column_menu)
        self.dock.search_clicked.connect(self.show_search_dialog)
        self.dock.updates_clicked.connect(self.show_update_box)

        #self.profile = ProfileDialog(self)
        #self.profile.show()
        #friend = SelectFriendDialog(self)
        self.update_box = UpdateBox(self)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._container, 1)
        layout.addWidget(self.dock)
        layout.setMargin(0)

        self.setLayout(layout)

    def __add_column(self, column_id):
        self.save_column(column_id)

    #================================================================
    # Tray icon
    #================================================================

    def __on_tray_click(self):
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

    #================================================================
    # Main methods
    #================================================================

    def load_image(self, filename, pixbuf=False):
        img_path = os.path.join(self.images_path, filename)
        if pixbuf:
            return QPixmap(img_path)
        return QImage(img_path)

    def get_image_path(self, filename):
        return os.path.join(self.images_path, filename)

    def update_container(self):
        accounts = self.get_registered_accounts()
        columns = self.get_registered_columns()

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
            self.download_stream(columns[0])

    def show_accounts_dialog(self):
        accounts = AccountsDialog(self)

    def show_column_menu(self, point):
        self.columns_menu = QMenu(self)

        available_columns = self.get_available_columns()
        accounts = self.get_all_accounts()

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
                        item.triggered.connect(partial(self.__add_column, column.id_))
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
            column_id = "%s-%s:%s" % (account_id, ColumnType.SEARCH, urllib2.quote(criteria))
            self.__add_column(column_id)

    def show_update_box(self):
        self.update_box.show()

    #================================================================
    # Hooks definitions
    #================================================================

    def after_save_account(self, account):
        self.account_registered.emit()

    def after_delete_account(self):
        self.account_deleted.emit()

    def after_delete_column(self, column_id):
        self._container.remove_column(column_id)
        self.update_container()
        # TODO: Enable timers
        #self.__remove_timer(column_id)

    def after_save_column(self, column_id):
        self._container.add_column(column_id)
        self.update_container()
        # TODO: Enable timers
        #self.download_stream(column)
        #self.__add_timer(column)

    def update_column(self, arg, data):
        column, notif, max_ = data

        # Notifications
        # FIXME
        count = len(arg)

        if count > 0:
            self._container.update_column(column.id_, arg)

    def after_update_status(self, account_id):
        self.update_box.done()

    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------

    def download_stream(self, column, notif=True):
        if self._container.is_updating(column.id_):
            return True

        last_id = self._container.start_updating(column.id_)
        count = self.core.get_max_statuses_per_column()

        self.worker.register(self.core.get_column_statuses, (column.account_id,
            column.slug, count, last_id), self.update_column,
            (column, notif, count))
        return True

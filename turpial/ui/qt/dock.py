# -*- coding: utf-8 -*-

# Qt dock for Turpial

from functools import partial

from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QSizePolicy

from PyQt4.QtCore import QPoint
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton

class Dock(QStatusBar):

    accounts_clicked = pyqtSignal()
    columns_clicked = pyqtSignal(QPoint)
    search_clicked = pyqtSignal()
    updates_clicked = pyqtSignal()
    messages_clicked = pyqtSignal()
    queue_clicked = pyqtSignal()
    filters_clicked = pyqtSignal()
    preferences_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()

    LOADING = -1
    EMPTY = 0
    WITH_ACCOUNTS = 1
    NORMAL = 2

    def __init__(self, base):
        QStatusBar.__init__(self)
        self.base = base
        self.status = self.LOADING

        style = "background-color: %s; border: 0px solid %s;" % (self.base.bgcolor, self.base.bgcolor)

        self.updates_button = ImageButton(base, 'dock-updates.png',
                i18n.get('update_status'))
        self.messages_button = ImageButton(base, 'dock-messages.png',
                i18n.get('send_direct_message'))
        self.search_button = ImageButton(base, 'dock-search.png',
                i18n.get('search'))
        self.settings_button = ImageButton(base, 'dock-preferences.png',
                i18n.get('settings'))
        self.settings_button.setStyleSheet("QPushButton { %s opacity: 128; }; QToolButton:hover { %s opacity: 255;}" % (style, style))

        self.updates_button.clicked.connect(self.__updates_clicked)
        self.messages_button.clicked.connect(self.__messages_clicked)
        self.search_button.clicked.connect(self.__search_clicked)
        self.settings_button.clicked.connect(self.__settings_clicked)

        separator = QWidget()
        separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        toolbar = QToolBar()
        toolbar.addWidget(self.settings_button)
        toolbar.addWidget(separator)
        toolbar.addWidget(self.search_button)
        toolbar.addWidget(self.messages_button)
        toolbar.addWidget(self.updates_button)
        toolbar.setMinimumHeight(30)
        toolbar.setContentsMargins(0, 0, 0, 0)
        toolbar.setStyleSheet("QToolBar { %s }" % style)

        self.addPermanentWidget(toolbar, 1)
        self.setSizeGripEnabled(False)

        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("QStatusBar { %s }" % style)
        self.loading()

    def __accounts_clicked(self):
        self.accounts_clicked.emit()

    def __columns_clicked(self):
        self.columns_clicked.emit(QCursor.pos())

    def __search_clicked(self):
        self.search_clicked.emit()

    def __updates_clicked(self):
        self.updates_clicked.emit()

    def __messages_clicked(self):
        self.messages_clicked.emit()

    def __queue_clicked(self):
        self.queue_clicked.emit()

    def __filters_clicked(self):
        self.filters_clicked.emit()

    def __preferences_clicked(self):
        self.preferences_clicked.emit()

    def __about_clicked(self):
        self.base.show_about_dialog()

    def __quit_clicked(self):
        self.quit_clicked.emit()

    def __settings_clicked(self):
        self.settings_menu = QMenu(self)

        accounts = QAction(i18n.get('accounts'), self)
        accounts.triggered.connect(partial(self.__accounts_clicked))

        queue = QAction(i18n.get('messages_queue'), self)
        queue.triggered.connect(partial(self.__queue_clicked))
        columns = QAction(i18n.get('columns'), self)

        filters = QAction(i18n.get('filters'), self)
        filters.triggered.connect(partial(self.__filters_clicked))
        preferences = QAction(i18n.get('preferences'), self)
        preferences.triggered.connect(partial(self.__preferences_clicked))
        about_turpial = QAction(i18n.get('about_turpial'), self)
        about_turpial.triggered.connect(partial(self.__about_clicked))
        quit = QAction(i18n.get('quit'), self)
        quit.triggered.connect(self.__quit_clicked)

        if self.status > self.EMPTY:
            columns_menu = self.base.build_columns_menu()
            columns.setMenu(columns_menu)
        elif self.status == self.EMPTY:
            queue.setEnabled(False)
            columns.setEnabled(False)
        elif self.status == self.LOADING:
            accounts.setEnabled(False)
            queue.setEnabled(False)
            columns.setEnabled(False)
            filters.setEnabled(False)
            preferences.setEnabled(False)

        self.settings_menu.addAction(accounts)
        self.settings_menu.addAction(columns)
        self.settings_menu.addAction(filters)
        self.settings_menu.addAction(queue)
        self.settings_menu.addSeparator()
        self.settings_menu.addAction(preferences)
        self.settings_menu.addSeparator()
        self.settings_menu.addAction(about_turpial)
        self.settings_menu.addAction(quit)
        self.settings_menu.exec_(QCursor.pos())

    def loading(self):
        self.updates_button.setEnabled(False)
        self.messages_button.setEnabled(False)
        self.search_button.setEnabled(False)
        self.status = self.LOADING

    def empty(self, with_accounts=None):
        self.updates_button.setEnabled(False)
        self.messages_button.setEnabled(False)
        self.search_button.setEnabled(False)
        if with_accounts:
            self.status = self.WITH_ACCOUNTS
        else:
            self.status = self.EMPTY


    def normal(self):
        self.updates_button.setEnabled(True)
        self.messages_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.status = self.NORMAL

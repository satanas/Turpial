# -*- coding: utf-8 -*-

# Qt dock for Turpial

from functools import partial

from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QHBoxLayout
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

    def __init__(self, base):
        QStatusBar.__init__(self)
        self.base = base

        bg_color = "#333"
        style = "background-color: %s; border: 0px solid %s;" % (bg_color, bg_color)

        self.updates_button = ImageButton(base, 'dock-updates.png',
                i18n.get('update_status'))
        self.messages_button = ImageButton(base, 'dock-messages.png',
                i18n.get('send_direct_message'))
        self.search_button = ImageButton(base, 'dock-search.png',
                i18n.get('search'))
        self.settings_button = ImageButton(base, 'dock-preferences.png',
                i18n.get('settings'))
        self.about_button = ImageButton(base, 'dock-about.png',
                i18n.get('about_turpial'))
        self.about_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.updates_button.clicked.connect(self.__updates_clicked)
        self.messages_button.clicked.connect(self.__messages_clicked)
        self.search_button.clicked.connect(self.__search_clicked)
        self.settings_button.clicked.connect(self.__settings_clicked)

        separator = QWidget()
        separator.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        toolbar = QToolBar()
        toolbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(self.settings_button)
        toolbar.addWidget(separator)
        toolbar.addWidget(self.search_button)
        toolbar.addWidget(self.messages_button)
        toolbar.addWidget(self.updates_button)
        toolbar.setStyleSheet("QToolBar { %s }" % style)
        toolbar.setMinimumHeight(24)
        self.addPermanentWidget(toolbar, 1)
        self.setStyleSheet("QStatusBar { %s }" % style)
        self.setContentsMargins(0, 0, 0, 0)

    def __build_settings_menu(self, with_accounts):
        menu = QMenu(self)

        accounts = QAction(i18n.get('add_accounts'), self)
        accounts.triggered.connect(partial(self.__accounts_clicked))

        columns = QAction(i18n.get('add_columns'), self)
        if with_accounts:
            columns_menu = self.base.build_columns_menu()
            columns.setMenu(columns_menu)
        else:
            columns.setEnabled(False)

        preferences = QAction(i18n.get('preferences'), self)
        about_turpial = QAction(i18n.get('about_turpial'), self)

        menu.addAction(accounts)
        menu.addAction(columns)
        menu.addSeparator()
        menu.addAction(preferences)
        menu.addSeparator()
        menu.addAction(about_turpial)
        return menu


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

    def __settings_clicked(self):
        self.settings_menu.exec_(QCursor.pos())

    def empty(self, with_accounts=None):
        self.updates_button.setEnabled(False)
        self.messages_button.setEnabled(False)
        self.settings_menu = self.__build_settings_menu(with_accounts)

    def normal(self):
        self.updates_button.setEnabled(True)
        self.messages_button.setEnabled(True)
        self.settings_menu = self.__build_settings_menu(True)

# -*- coding: utf-8 -*-

# Qt dock for Turpial

from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QHBoxLayout

from PyQt4.QtCore import QPoint
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton

class Dock(QStatusBar):

    accounts_clicked = pyqtSignal()
    columns_clicked = pyqtSignal(QPoint)
    search_clicked = pyqtSignal()
    updates_clicked = pyqtSignal()

    def __init__(self, base):
        QStatusBar.__init__(self)
        self.base = base

        bg_color = "#333"
        style = "background-color: %s; border: 0px solid %s;" % (bg_color, bg_color)

        self.updates_button = ImageButton(base, 'dock-updates.png',
                i18n.get('update_status'))
        self.messages_button = ImageButton(base, 'dock-messages.png',
                i18n.get('send_direct_message'))
        self.columns_button = ImageButton(base, 'dock-columns.png',
                i18n.get('add_columns'))
        self.accounts_button = ImageButton(base, 'dock-accounts.png',
                i18n.get('add_accounts'))
        self.search_button = ImageButton(base, 'dock-search.png',
                i18n.get('search'))
        self.preferences_button = ImageButton(base, 'dock-preferences.png',
                i18n.get('open_preferences_dialog'))
        self.about_button = ImageButton(base, 'dock-about.png',
                i18n.get('about_turpial'))

        self.columns_button.clicked.connect(self.__columns_clicked)
        self.accounts_button.clicked.connect(self.__accounts_clicked)
        self.search_button.clicked.connect(self.__search_clicked)
        self.updates_button.clicked.connect(self.__updates_clicked)

        toolbar = QToolBar()
        toolbar.addWidget(self.about_button)
        toolbar.addWidget(self.preferences_button)
        toolbar.addWidget(self.search_button)
        toolbar.addWidget(self.accounts_button)
        toolbar.addWidget(self.columns_button)
        toolbar.addWidget(self.messages_button)
        toolbar.addWidget(self.updates_button)
        toolbar.setStyleSheet("QToolBar { %s }" % style)
        toolbar.setMinimumHeight(24)
        self.addPermanentWidget(toolbar)
        self.setStyleSheet("QStatusBar { %s }" % style)

    def __accounts_clicked(self):
        self.accounts_clicked.emit()

    def __columns_clicked(self):
        self.columns_clicked.emit(QCursor.pos())

    def __search_clicked(self):
        self.search_clicked.emit()

    def __updates_clicked(self):
        self.updates_clicked.emit()

    def empty(self, with_accounts=None):
        self.updates_button.setEnabled(False)
        self.messages_button.setEnabled(False)
        if with_accounts:
            self.columns_button.setEnabled(True)
        else:
            self.columns_button.setEnabled(False)

    def normal(self):
        self.updates_button.setEnabled(True)
        self.messages_button.setEnabled(True)
        self.columns_button.setEnabled(True)

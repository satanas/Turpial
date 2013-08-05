# -*- coding: utf-8 -*-

# Qt dock for Turpial

from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QHBoxLayout

from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton

class Dock(QStatusBar):

    accounts_clicked = pyqtSignal()

    def __init__(self, base):
        QStatusBar.__init__(self)
        self.base = base

        bg_color = "#333"
        style = "background-color: %s; border: 0px solid %s;" % (bg_color, bg_color)

        self.updates_btn = ImageButton(base, 'dock-updates.png',
                i18n.get('update_status'))
        self.messages_btn = ImageButton(base, 'dock-messages.png',
                i18n.get('send_direct_message'))
        self.columns_btn = ImageButton(base, 'dock-columns.png',
                i18n.get('add_columns'))
        self.accounts_btn = ImageButton(base, 'dock-accounts.png',
                i18n.get('add_accounts'))
        self.accounts_btn.clicked.connect(self.__accounts_clicked)
        self.search_btn = ImageButton(base, 'dock-search.png',
                i18n.get('search'))
        self.preferences_btn = ImageButton(base, 'dock-preferences.png',
                i18n.get('open_preferences_dialog'))
        self.about_btn = ImageButton(base, 'dock-about.png',
                i18n.get('about_turpial'))

        toolbar = QToolBar()
        toolbar.addWidget(self.about_btn)
        toolbar.addWidget(self.preferences_btn)
        toolbar.addWidget(self.search_btn)
        toolbar.addWidget(self.accounts_btn)
        toolbar.addWidget(self.columns_btn)
        toolbar.addWidget(self.messages_btn)
        toolbar.addWidget(self.updates_btn)
        toolbar.setStyleSheet("QToolBar { %s }" % style)
        toolbar.setMinimumHeight(24)
        self.addPermanentWidget(toolbar)
        self.setStyleSheet("QStatusBar { %s }" % style)

    def __accounts_clicked(self):
        self.accounts_clicked.emit()

    def empty(self, with_accounts=None):
        self.updates_btn.setEnabled(False)
        self.messages_btn.setEnabled(False)
        if with_accounts:
            self.columns_btn.setEnabled(True)
        else:
            self.columns_btn.setEnabled(False)

    def normal(self):
        self.updates_btn.setEnabled(True)
        self.messages_btn.setEnabled(True)
        self.columns_btn.setEnabled(True)

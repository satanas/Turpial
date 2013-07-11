# -*- coding: utf-8 -*-

# Qt dock for Turpial

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QToolButton
from PyQt4.QtGui import QToolBar

from turpial.ui.lang import i18n

class Dock(QStatusBar):
    def __init__(self, base):
        QStatusBar.__init__(self)
        self.base = base

        bg_color = "#333"
        style = "background-color: %s; border: 0px solid %s;" % (bg_color, bg_color)

        self.updates_btn = DockButton(base, 'dock-updates.png',
                i18n.get('update_status'))
        self.messages_btn = DockButton(base, 'dock-messages.png',
                i18n.get('send_direct_message'))
        self.columns_btn = DockButton(base, 'dock-columns.png',
                i18n.get('add_columns'))
        self.accounts_btn = DockButton(base, 'dock-accounts.png',
                i18n.get('add_accounts'))
        self.search_btn = DockButton(base, 'dock-search.png',
                i18n.get('search'))
        self.preferences_btn = DockButton(base, 'dock-preferences.png',
                i18n.get('open_preferences_dialog'))
        self.about_btn = DockButton(base, 'dock-about.png',
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


class DockButton(QToolButton):
    def __init__(self, base, image, tooltip):
        QToolButton.__init__(self)

        icon = QIcon(base.get_image_path(image))
        self.setIcon(icon)
        self.setToolTip(tooltip)
        self.setMaximumSize(24, 24)

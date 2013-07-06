# -*- coding: utf-8 -*-

# Qt dock for Turpial

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QStatusBar
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QToolButton
from PyQt4.QtGui import QToolBar

class Dock(QStatusBar):
    def __init__(self, base):
        QStatusBar.__init__(self)
        self.base = base

        bg_color = "#333"
        style = "background-color: %s; border: 0px solid %s;" % (bg_color, bg_color)

        updates_icon = QIcon(base.get_image_path('dock-updates.png'))
        self.updates_btn = QToolButton()
        self.updates_btn.setIcon(updates_icon)
        self.updates_btn.setAutoRaise(True)
        self.updates_btn.setMaximumSize(24, 24)

        preferences_icon = QIcon(base.get_image_path('dock-preferences.png'))
        self.preferences_btn = QToolButton()
        self.preferences_btn.setIcon(preferences_icon)
        self.preferences_btn.setAutoRaise(False)
        self.preferences_btn.setMaximumSize(24, 24)

        toolbar = QToolBar()
        toolbar.addWidget(self.preferences_btn)
        toolbar.addWidget(self.updates_btn)
        toolbar.setStyleSheet("QToolBar { %s }" % style)
        toolbar.setMinimumHeight(24)
        self.addPermanentWidget(toolbar)
        self.setStyleSheet("QStatusBar { %s }" % style)



# -*- coding: utf-8 -*-

# Qt widget to implement statuses column in Turpial

#from PyQt4 import QtCore
from PyQt4.QtCore import QSize

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QProgressBar
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton

class StatusesColumn(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.setMinimumWidth(250)

        icon = QLabel()
        icon.setPixmap(base.load_image('twitter.png', True))

        caption = QLabel('satanas82 :: timeline')

        close_button = ImageButton(base, 'action-delete.png',
                i18n.get('delete_column'))

        header = QHBoxLayout()
        header.addWidget(icon)
        header.addWidget(caption, 1)
        header.addWidget(close_button)

        self.loader = QProgressBar()
        self.loader.setMinimum(0)
        self.loader.setMaximum(0)
        self.loader.setMaximumHeight(6)
        self.loader.setTextVisible(False)

        self._list = QListView()

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self.loader)
        layout.addWidget(self._list)

        self.setLayout(layout)

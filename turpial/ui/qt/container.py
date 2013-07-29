# -*- coding: utf-8 -*-

# Qt container for all columns in Turpial

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.column import StatusesColumn

class Container(QVBoxLayout):
    def __init__(self, base):
        QVBoxLayout.__init__(self)
        self.base = base
        self.child = None
        self.columns = {}

    def empty(self, with_accounts=None):
        if self.child:
            del(self.child)

        image = self.base.load_image('logo.png', True)
        logo = QLabel()
        logo.setPixmap(image)
        logo.setAlignment(Qt.AlignCenter)
        logo.setContentsMargins(0, 80, 0, 0)

        welcome = QLabel()
        welcome.setText(i18n.get('welcome'))
        welcome.setAlignment(Qt.AlignCenter)

        message = QLabel()
        if with_accounts:
            message.setText(i18n.get('add_some_columns'))
        else:
            message.setText(i18n.get('add_new_account'))
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)

        self.child = QVBoxLayout()
        self.child.addWidget(logo, 1)
        self.child.addWidget(welcome)
        self.child.addWidget(message)
        self.child.setSpacing(10)
        self.child.setContentsMargins(30, 0, 30, 60)

        self.addLayout(self.child)

    def normal(self):
        if self.child:
            del(self.child)

        column1 = StatusesColumn(self.base, True)
        column2 = StatusesColumn(self.base)
        column3 = StatusesColumn(self.base)

        hbox = QHBoxLayout()
        hbox.addWidget(column1, 1)
        hbox.addWidget(column2, 1)
        hbox.addWidget(column3, 1)

        viewport = QWidget()
        viewport.setLayout(hbox)

        self.child = QScrollArea()
        self.child.setWidgetResizable(True)
        self.child.setWidget(viewport)

        self.addWidget(self.child, 1)


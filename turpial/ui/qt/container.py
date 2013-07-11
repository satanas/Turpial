# -*- coding: utf-8 -*-

# Qt container for all columns in Turpial

from PyQt4 import QtCore
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout

from turpial.ui.lang import i18n

class Container(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.child = None
        self.columns = {}

    def empty(self, with_accounts=None):
        if self.child:
            self.removeWidget(self.child)

        image = self.base.load_image('logo.png', True)
        logo = QLabel()
        logo.setPixmap(image)
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setContentsMargins(0, 80, 0, 0)

        welcome = QLabel()
        welcome.setText(i18n.get('welcome'))
        welcome.setAlignment(QtCore.Qt.AlignCenter)

        message = QLabel()
        if with_accounts:
            message.setText(i18n.get('add_some_columns'))
        else:
            message.setText(i18n.get('add_new_account'))
        message.setAlignment(QtCore.Qt.AlignCenter)
        message.setWordWrap(True)

        self.child = QVBoxLayout()
        self.child.addWidget(logo, 1)
        self.child.addWidget(welcome)
        self.child.addWidget(message)
        self.child.setSpacing(10)
        self.child.setContentsMargins(30, 0, 30, 60)

        self.setLayout(self.child)


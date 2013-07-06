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

    def empty(self):
        if self.child:
            self.removeWidget(self.child)

        image = self.base.load_image('logo.png', True)
        logo = QLabel()
        logo.setPixmap(image)
        logo.setAlignment(QtCore.Qt.AlignCenter)
        logo.setContentsMargins(0, 80, 0, 0)
        #splash = QtGui.QHBoxLayout()
        #splash.addWidget(logo, 1)

        welcome = QLabel()
        welcome.setText(i18n.get('welcome'))
        welcome.setAlignment(QtCore.Qt.AlignCenter)

        message = QLabel()
        message.setText(i18n.get('create_new_account'))
        message.setAlignment(QtCore.Qt.AlignCenter)

        #if len(self.base.get_accounts_list()) > 0:
        #    no_accounts.set_markup(i18n.get('no_registered_columns'))
        #else:
        #    no_accounts.set_markup(i18n.get('no_active_accounts'))

        self.child = QVBoxLayout()
        self.child.addWidget(logo, 1)
        self.child.addWidget(welcome)
        self.child.addWidget(message)
        self.child.setSpacing(10)
        self.child.setContentsMargins(30, 0, 30, 60)

        self.setLayout(self.child)


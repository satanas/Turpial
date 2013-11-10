# -*- coding: utf-8 -*-

# Qt about dialog for Turpial

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ModalDialog

from turpial import VERSION


class AboutDialog(ModalDialog):
    def __init__(self, base):
        ModalDialog.__init__(self, 320, 250)
        self.setWindowTitle(i18n.get('about_turpial'))

        icon = QLabel()
        icon.setPixmap(base.load_image('turpial.png', True))
        icon.setAlignment(Qt.AlignCenter)

        app_name = QLabel("<b>Turpial %s</b>" % VERSION)
        app_name.setAlignment(Qt.AlignCenter)
        app_description = QLabel(i18n.get('about_description'))
        app_description.setAlignment(Qt.AlignCenter)
        copyright = QLabel('Copyleft (C) 2009 - 2013 Wil Alvarez')
        copyright.setAlignment(Qt.AlignCenter)

        close_button = QPushButton(i18n.get('close'))
        close_button.clicked.connect(self.__on_close)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.setSpacing(4)
        button_box.addWidget(close_button)

        vbox = QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addWidget(icon, 1)
        vbox.addWidget(app_name)
        vbox.addWidget(app_description)
        vbox.addWidget(copyright)
        vbox.addLayout(button_box)

        self.setLayout(vbox)
        self.exec_()

    def __on_close(self):
        self.close()

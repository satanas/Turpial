# -*- coding: utf-8 -*-

# Qt OAuth dialog for Turpial

from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize

from turpial.ui.lang import i18n


class OAuthDialog(QDialog):
    def __init__(self, base, url):
        QDialog.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('authorize_turpial'))
        self.resize(800, 550)
        self.setModal(True)

        self.webview = QWebView()
        qurl = QUrl(url)
        self.webview.setUrl(qurl)

        message = QLabel(i18n.get('copy_the_pin'))
        #message.setAlignment(Qt.AlignRight)

        self.pin = QLineEdit()
        self.pin.setPlaceholderText(i18n.get('type_the_pin'))

        authorize_btn = QPushButton(i18n.get('save'))
        authorize_btn.clicked.connect(self.accept)

        widgets_box = QHBoxLayout()
        widgets_box.setSpacing(3)
        widgets_box.setContentsMargins(3, 3, 3, 3)
        widgets_box.addWidget(message, 1)
        widgets_box.addWidget(self.pin)
        widgets_box.addWidget(authorize_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        layout.addLayout(widgets_box)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.exec_()

# -*- coding: utf-8 -*-

# Qt OAuth dialog for Turpial

from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import HLine


class OAuthDialog(QDialog):
    def __init__(self, account_dialog, url):
        QDialog.__init__(self)
        self.account_dialog = account_dialog
        self.setWindowTitle(i18n.get('authorize_turpial'))
        self.resize(800, 550)
        self.setModal(True)

        self.webview = QWebView()
        qurl = QUrl(url)
        self.webview.setUrl(qurl)

        message = QLabel(i18n.get('copy_the_pin'))
        message.setStyleSheet("QLabel { color: #fff; font-size: 14px;}")

        self.pin = QLineEdit()
        self.pin.setPlaceholderText(i18n.get('type_the_pin'))

        authorize_btn = QPushButton(i18n.get('authorize'))
        authorize_btn.clicked.connect(self.accept)

        open_in_browser_btn = QPushButton(i18n.get('open_in_browser'))
        open_in_browser_btn.clicked.connect(self.__external_open)

        widgets_box = QHBoxLayout()
        widgets_box.setSpacing(3)
        widgets_box.setContentsMargins(10, 10, 10, 10)
        widgets_box.addWidget(message, 1)
        widgets_box.addWidget(self.pin)
        widgets_box.addWidget(open_in_browser_btn)
        widgets_box.addWidget(authorize_btn)
        bgcolor = self.account_dialog.base.theme['header']['background_color']
        fgcolor = self.account_dialog.base.theme['header']['text_color']
        style = "background-color: %s; border: 0px solid %s; color: %s;" % (bgcolor, bgcolor, text_color)
        self.setStyleSheet("QDialog { %s }" % style)

        layout = QVBoxLayout()
        layout.addWidget(self.webview)
        #layout.addWidget(HLine(2))
        layout.addLayout(widgets_box)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.exec_()

    def __external_open(self):
        self.account_dialog.base.open_in_browser(str(self.webview.url()))
        self.reject()

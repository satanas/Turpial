# -*- coding: utf-8 -*-

# Qt image view for Turpial

from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QGridLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n
from turpial.ui.qt.webview import ImageWebView
from turpial.ui.qt.loader import BarLoadIndicator


class ImageView(QWidget):

    def __init__(self, base, url):
        QWidget.__init__(self)

        self.setWindowTitle(i18n.get('imageview'))
        self.setBaseSize(350, 350)

        self.base = base
        self.loader = BarLoadIndicator()
        self.loader.setVisible(True)

        self.webview = ImageWebView(self.base)
        self.webview.update_image(url)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.loader)
        layout.addWidget(self.webview)

        self.setLayout(layout)
        self.show()

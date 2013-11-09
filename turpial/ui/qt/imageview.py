# -*- coding: utf-8 -*-

# Qt image view for Turpial

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QPalette
from PyQt4.QtGui import QSizePolicy
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QGridLayout

from PyQt4.QtCore import Qt

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import Window
from turpial.ui.qt.loader import BarLoadIndicator


class ImageView(Window):
    def __init__(self, base):
        Window.__init__(self, base, i18n.get('image_preview'))

        self.loader = BarLoadIndicator()

        self.view = QLabel()
        self.view.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.view.setScaledContents(True)

        scroll_area = QScrollArea()
        scroll_area.setBackgroundRole(QPalette.Dark)
        scroll_area.setWidget(self.view)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.error_label = QLabel(i18n.get('error_loading_image'))
        self.error_label.setAlignment(Qt.AlignHCenter)
        self.error_label.setStyleSheet("QLabel {background-color: #ffecec;}")

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.loader)
        layout.addWidget(self.error_label)
        layout.addWidget(scroll_area)

        self.setLayout(layout)
        self.__clear()

    def __clear(self):
        self.resize(350, 350)
        self.view.setPixmap(QPixmap())

    def closeEvent(self, event):
        event.ignore()
        self.__clear()
        self.hide()

    def start_loading(self):
        self.loader.setVisible(True)
        self.error_label.setVisible(False)
        self.show()

    def loading_finished(self, url):
        self.loader.setVisible(False)
        pix = self.base.load_image(url, True)
        self.view.setPixmap(pix)
        self.view.adjustSize()
        self.resize(pix.width() + 2, pix.height() + 2)
        self.show()

    def error(self):
        self.loader.setVisible(False)
        self.error_label.setVisible(True)

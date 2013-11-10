# -*- coding: utf-8 -*-

# Qt util widgets for Turpial

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QFrame
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QToolButton

class ImageButton(QToolButton):
    def __init__(self, base, image, tooltip):
        QToolButton.__init__(self)
        icon = QIcon(base.get_image_path(image))
        self.setIcon(icon)
        self.setToolTip(tooltip)
        self.setMaximumSize(24, 24)

class HLine(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setMinimumHeight(20)

class VLine(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setMinimumWidth(5)

class ToggleButton(QToolButton):
    def __init__(self, base, image, text=None, tooltip=None):
        QToolButton.__init__(self)
        icon = QIcon(base.get_image_path(image))
        self.setIcon(icon)
        self.setCheckable(True)
        if text:
            self.setText(text)
            self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            self.setMaximumHeight(24)
        else:
            self.setMaximumSize(24, 24)

        if tooltip:
            self.setToolTip(tooltip)

class ModalDialog(QDialog):
    def __init__(self, width, height):
        QDialog.__init__(self)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setModal(True)

class Window(QWidget):
    def __init__(self, base, title):
        QWidget.__init__(self)
        self.setWindowTitle(title)
        self.base = base

    def __center_on_parent(self):
        geo = self.base.geometry()
        cx = geo.x() + (geo.width() / 2)
        cy = geo.y() + (geo.height() / 2)
        geo2 = self.geometry()
        fx = cx - (geo2.width() / 2)
        fy = cy - (geo2.height() / 2)
        self.setGeometry(fx,fy, geo2.width(), geo2.height())

    def show(self):
        QWidget.show(self)
        self.__center_on_parent()

class ErrorLabel(QLabel):
    def __init__(self):
        QLabel.__init__(self)

        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        self.setStyleSheet("QLabel {color: #f00}")

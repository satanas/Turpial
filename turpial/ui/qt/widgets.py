# -*- coding: utf-8 -*-

# Qt util widgets for Turpial

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFrame
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

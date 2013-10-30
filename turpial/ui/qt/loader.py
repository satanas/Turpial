# -*- coding: utf-8 -*-

# Qt loaders for Turpial

from PyQt4.QtGui import QProgressBar

class BarLoadIndicator(QProgressBar):
    def __init__(self):
        QProgressBar.__init__(self)
        self.setMinimum(0)
        self.setMaximum(0)
        self.setMaximumHeight(6)
        self.setTextVisible(False)

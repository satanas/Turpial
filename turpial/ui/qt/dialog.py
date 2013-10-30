# -*- coding: utf-8 -*-

# Qt modal dialog for Turpial

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

class ModalDialog(QDialog):
    def __init__(self, width, height):
        QDialog.__init__(self)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setModal(True)

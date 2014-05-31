# -*- coding: utf-8 -*-

# Qt shortcuts for Turpial

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QShortcut
from PyQt4.QtGui import QKeySequence

class Shortcuts:
    def __init__(self, base):
        Shortcut.base = base
        self.__shortcuts = {
            'accounts': Shortcut(Qt.CTRL + Qt.Key_A, 'A'),
            'filters': Shortcut(Qt.CTRL + Qt.Key_F, 'F'),
            'tweet': Shortcut(Qt.CTRL + Qt.Key_T, 'T'),
            'message': Shortcut(Qt.CTRL + Qt.Key_M, 'M'),
            'search': Shortcut(Qt.CTRL + Qt.Key_S, 'S'),
            'queue': Shortcut(Qt.CTRL + Qt.Key_U, 'U'),
            'preferences': Shortcut(Qt.CTRL + Qt.Key_Comma, ','),
            'quit': Shortcut(Qt.CTRL + Qt.Key_Q, 'Q'),
            'move_column_right': Shortcut(Qt.Key_Tab, 'Tab'),
            'move_column_left': Shortcut(Qt.SHIFT + Qt.Key_Tab, 'Shift + Tab'),
        }

    def __iter__(self):
        return self.__shortcuts.iteritems()

    def get(self, action):
        return self.__shortcuts[action]

class Shortcut(QObject):
    activated = pyqtSignal()

    def __init__(self, sequence, key, modifier=None):
        QObject.__init__(self)
        self.sequence = QKeySequence(sequence)
        self.caption = self.base.get_shortcut_string(key, modifier)
        self.action = QAction(self.base)
        self.action.setShortcutContext(Qt.ApplicationShortcut)
        self.action.setShortcut(self.sequence)
        self.action.triggered.connect(self.__triggered)

    def __triggered(self):
        self.activated.emit()

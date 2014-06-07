# -*- coding: utf-8 -*-

# Qt shortcuts for Turpial

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QObject
from PyQt4.QtCore import pyqtSignal

from PyQt4.QtGui import QAction
from PyQt4.QtGui import QShortcut
from PyQt4.QtGui import QKeySequence

from libturpial.common import OS_MAC
from libturpial.common.tools import detect_os

class Shortcuts:
    def __init__(self, base):
        Shortcut.base = base
        self.__shortcuts = {
            'accounts': Shortcut(Qt.CTRL, Qt.Key_A),
            'filters': Shortcut(Qt.CTRL, Qt.Key_F),
            'tweet': Shortcut(Qt.CTRL, Qt.Key_T),
            'message': Shortcut(Qt.CTRL, Qt.Key_M),
            'search': Shortcut(Qt.CTRL, Qt.Key_S),
            'queue': Shortcut(Qt.CTRL, Qt.Key_U),
            'preferences': Shortcut(Qt.CTRL, Qt.Key_Comma),
            'quit': Shortcut(Qt.CTRL, Qt.Key_Q),
            'move_column_right': Shortcut(None, Qt.Key_Tab),
            'move_column_left': Shortcut(Qt.SHIFT, Qt.Key_Tab),
            'post': Shortcut(Qt.CTRL, Qt.Key_Enter, True),
            'add_to_queue': Shortcut(Qt.CTRL, Qt.Key_P, True),
        }

    def __iter__(self):
        return self.__shortcuts.iteritems()

    def get(self, action):
        return self.__shortcuts[action]

class Shortcut(QObject):
    activated = pyqtSignal()

    def __init__(self, modifier, key, ghost=False):
        QObject.__init__(self)
        self.ghost = ghost
        sequence = modifier + key if modifier else key
        self.sequence = QKeySequence(sequence)

        self.action = QAction(self.base)
        self.action.setShortcutContext(Qt.ApplicationShortcut)
        self.action.setShortcut(self.sequence)
        self.action.triggered.connect(self.__triggered)

        self.caption = self.__get_caption(modifier, key)

    def __triggered(self):
        self.activated.emit()

    def __get_caption(self, modifier, key):
        values = []
        if modifier == Qt.SHIFT:
            values.append(self.base.shift_key)
        elif modifier == Qt.CTRL:
            values.append(self.base.command_key)
        values.append(str(QKeySequence(key).toString()))

        return self.base.command_separator.join(values)

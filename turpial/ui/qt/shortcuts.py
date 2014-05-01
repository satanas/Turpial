# -*- coding: utf-8 -*-

# Qt shortcuts for Turpial

from PyQt4.QtCore import Qt

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
            'queue': Shortcut(Qt.CTRL + Qt.Key_F, 'F'),
            'preferences': Shortcut(Qt.CTRL + Qt.Key_Comma, ','),
            'quit': Shortcut(Qt.CTRL + Qt.Key_Q, 'Q'),
        }

    def __iter__(self):
        return self.__shortcuts.iteritems()

    def get(self, action):
        return self.__shortcuts[action]

class Shortcut:
    def __init__(self, sequence, caption):
        self.sequence = QKeySequence(sequence)
        self.caption = self.base.get_shortcut_string(caption)


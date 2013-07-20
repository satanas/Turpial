# -*- coding: utf-8 -*-

# Qt select friend dialog for Turpial

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.dialog import ModalDialog
from turpial.ui.qt.widgets import ImageButton


class SelectFriendDialog(ModalDialog):
    def __init__(self, base):
        ModalDialog.__init__(self, 290, 60)
        self.base = base
        self.setWindowTitle(i18n.get('select_friend'))

        completer = QCompleter(['one', 'two', 'carlos', 'maria',
            'ana', 'carolina', 'alberto', 'pedro', 'tomas'])
        label = QLabel('@')
        friend = QLineEdit()
        friend.setCompleter(completer)
        select_button = QPushButton(i18n.get('select'))
        load_button = ImageButton(base, 'action-status-menu.png',
                i18n.get('load_friends_list'))

        form = QHBoxLayout()
        form.addWidget(label)
        form.addWidget(friend)
        form.addWidget(select_button)
        form.addWidget(load_button)
        form.setContentsMargins(10, 10, 10, 5)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.exec_()

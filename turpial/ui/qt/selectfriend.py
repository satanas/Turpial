# -*- coding: utf-8 -*-

# Qt select friend dialog for Turpial

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QFormLayout, QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ModalDialog

from libturpial.common.tools import get_protocol_from, get_username_from


class SelectFriendDialog(ModalDialog):
    def __init__(self, base):
        ModalDialog.__init__(self, 290, 110)
        self.base = base
        self.setWindowTitle(i18n.get('select_friend_to_send_message'))

        self.accounts_combo = QComboBox()
        accounts = self.base.core.get_registered_accounts()
        for account in accounts:
            protocol = get_protocol_from(account.id_)
            icon = QIcon(base.get_image_path('%s.png' % protocol))
            self.accounts_combo.addItem(icon, get_username_from(account.id_), account.id_)

        completer = QCompleter(self.base.load_friends_list())
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.friend = QLineEdit()
        self.friend.setCompleter(completer)
        select_button = QPushButton(i18n.get('select'))
        select_button.clicked.connect(self.__validate)

        friend_caption = "%s (@)" % i18n.get('friend')
        form = QFormLayout()
        form.addRow(friend_caption, self.friend)
        form.addRow(i18n.get('account'), self.accounts_combo)
        form.setContentsMargins(30, 10, 10, 5)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        button = QPushButton(i18n.get('search'))
        button_box = QHBoxLayout()
        button_box.addStretch(0)
        button_box.addWidget(select_button)
        button_box.setContentsMargins(0, 0, 15, 15)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(button_box)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        #load_button = ImageButton(base, 'action-status-menu.png',
        #        i18n.get('load_friends_list'))

        self.exec_()

    def __validate(self):
        if self.get_username() != '':
            self.accept()


    def get_account(self):
        index = self.accounts_combo.currentIndex()
        return str(self.accounts_combo.itemData(index).toPyObject())

    def get_username(self):
        return str(self.friend.text())

# -*- coding: utf-8 -*-

# Qt search dialog for Turpial

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QFormLayout, QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt

from turpial.ui.lang import i18n

from libturpial.common.tools import get_protocol_from, get_username_from


class SearchDialog(QDialog):
    def __init__(self, base):
        QDialog.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('search'))
        self.setFixedSize(270, 110)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
        self.setModal(True)

        self.accounts_combo = QComboBox()
        accounts = self.base.core.get_registered_accounts()
        for account in accounts:
            protocol = get_protocol_from(account.id_)
            icon = QIcon(base.get_image_path('%s.png' % protocol))
            self.accounts_combo.addItem(icon, get_username_from(account.id_), account.id_)

        self.criteria = QLineEdit()
        self.criteria.setToolTip(i18n.get('criteria_tooltip'))

        form = QFormLayout()
        form.addRow(i18n.get('criteria'), self.criteria)
        form.addRow(i18n.get('account'), self.accounts_combo)
        form.setContentsMargins(30, 10, 10, 5)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        button = QPushButton(i18n.get('search'))
        button_box = QHBoxLayout()
        button_box.addStretch(0)
        button_box.addWidget(button)
        button_box.setContentsMargins(0, 0, 15, 15)

        button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(button_box)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.criteria.setFocus()

        self.exec_()

    def get_criteria(self):
        return self.criteria.text()

    def get_account(self):
        index = self.accounts_combo.currentIndex()
        return self.accounts_combo.itemData(index)


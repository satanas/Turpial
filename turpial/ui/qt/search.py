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


class SearchDialog(QDialog):
    def __init__(self, base):
        QDialog.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('search'))
        self.setFixedSize(270, 110)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
        self.setModal(True)

        icon = QIcon(base.get_image_path('twitter.png'))
        accounts = QComboBox()
        accounts.addItem(icon, 'satanas82')
        accounts.addItem(icon, 'turpialve')

        criteria = QLineEdit()
        criteria.setToolTip(i18n.get('criteria_tooltip'))

        form = QFormLayout()
        form.addRow(i18n.get('account'), accounts)
        form.addRow(i18n.get('criteria'), criteria)
        form.setContentsMargins(30, 10, 10, 5)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        button = QPushButton(i18n.get('search'))
        button_box = QHBoxLayout()
        button_box.addStretch(0)
        button_box.addWidget(button)
        button_box.setContentsMargins(0, 0, 15, 15)

        layout = QVBoxLayout()
        layout.addLayout(form)
        layout.addLayout(button_box)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.exec_()

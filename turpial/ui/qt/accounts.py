# -*- coding: utf-8 -*-

# Qt account manager for Turpial

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QToolButton
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QListWidgetItem

from PyQt4.QtCore import QSize
from PyQt4.QtCore import Qt

from turpial.ui.lang import i18n


class AccountsDialog(QDialog):
    def __init__(self, base):
        QDialog.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('accounts'))
        self.resize(380,325)
        self.setModal(True)

        account1 = QListWidgetItem("satanas82\nTwitter")
        account1.setIcon(QIcon(base.load_image('unknown.png', True)))

        account2 = QListWidgetItem("TurpialVe\nTwitter")
        account2.setIcon(QIcon(base.load_image('unknown.png', True)))

        listwidget = QListWidget()
        listwidget.setIconSize(QSize(48, 48))
        listwidget.setSpacing(5)
        listwidget.addItem(account1)
        listwidget.addItem(account2)

        twitter_btn = QToolButton()
        twitter_btn.setText('Connect to Twitter')
        #twitter_btn.setToolTip(tooltip)
        identica_btn = QToolButton()
        identica_btn.setText('Connect to Identi.ca')

        toolbar = QToolBar()
        toolbar.addWidget(twitter_btn)
        toolbar.addWidget(identica_btn)
        toolbar.setOrientation(Qt.Vertical)

        layout = QHBoxLayout()
        layout.addWidget(listwidget)
        layout.addWidget(toolbar)
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)

        self.exec_()



    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True

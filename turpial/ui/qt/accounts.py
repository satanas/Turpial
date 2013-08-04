# -*- coding: utf-8 -*-

# Qt account manager for Turpial

import os

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QToolBar
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QToolButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtGui import QStyledItemDelegate

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QRect

from turpial.ui.lang import i18n
from turpial.ui.qt.dialog import ModalDialog

from libturpial.common.tools import get_protocol_from, get_username_from

USERNAME_FONT = QFont("Helvetica", 14)
PROTOCOL_FONT = QFont("Helvetica", 11)

class AccountsDialog(ModalDialog):
    def __init__(self, base):
        ModalDialog.__init__(self, 380,325)
        self.base = base
        self.setWindowTitle(i18n.get('accounts'))

        self._list = QListView()
        self._list.setResizeMode(QListView.Adjust)
        self._list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        model = QStandardItemModel()
        self._list.setModel(model)
        account_delegate = AccountDelegate(base)
        self._list.setItemDelegate(account_delegate)

        accounts = base.get_registered_accounts()
        for account in accounts:
            item = QStandardItem()
            filepath = os.path.join(self.base.images_path, 'unknown.png')
            item.setData(filepath, AccountDelegate.AvatarRole)
            item.setData(get_username_from(account.id_), AccountDelegate.UsernameRole)
            item.setData(get_protocol_from(account.id_).capitalize(), AccountDelegate.ProtocolRole)
            model.appendRow(item)

        twitter_btn = QToolButton()
        twitter_btn.setText('Connect to Twitter')
        twitter_btn.setIcon(QIcon(base.load_image('twitter.png', True)))
        twitter_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        twitter_btn.setToolTip(i18n.get('create_a_twitter_account'))

        identica_btn = QToolButton()
        identica_btn.setText('Connect to Identi.ca')
        identica_btn.setIcon(QIcon(base.load_image('identica.png', True)))
        identica_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        #identica_btn.setToolTip(tooltip)
        # TODO: Enable when identi.ca support is ready
        identica_btn.setEnabled(False)

        toolbar = QToolBar()
        toolbar.addWidget(twitter_btn)
        toolbar.addWidget(identica_btn)
        toolbar.setMinimumHeight(24)
        toolbar.setOrientation(Qt.Vertical)
        toolbar.setContentsMargins(10, 0, 10, 0)

        layout = QHBoxLayout()
        layout.addWidget(self._list)
        layout.addWidget(toolbar)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.exec_()

    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True

class AccountDelegate(QStyledItemDelegate):
    UsernameRole = Qt.UserRole + 100
    ProtocolRole = Qt.UserRole + 101
    AvatarRole = Qt.UserRole + 102

    AVATAR_SIZE = 48
    BOX_MARGIN = 4
    TEXT_MARGIN = 0

    def __init__(self, base):
        QStyledItemDelegate.__init__(self)
        self.avatar = None

    def sizeHint(self, option, index):
        height = self.AVATAR_SIZE + (self.BOX_MARGIN * 2)
        self.size = QSize(option.rect.width(), height)
        return self.size

    def paint(self, painter, option, index):
        painter.save()

        selected = False
        cell_width = self.size.width()

        rect = option.rect
        rect.width = self.size.width()
        rect.height = self.size.height()
        protocol_color = "999"
        if option.state & QStyle.State_Selected:
            painter.fillRect(rect, option.palette.highlight())
            protocol_color = "ddd"
            selected = True

        # Draw avatar
        if not self.avatar:
            avatar_filepath = index.data(self.AvatarRole).toPyObject()
            self.avatar = QPixmap(avatar_filepath)
        x = option.rect.left() + self.BOX_MARGIN
        y = option.rect.top() + self.BOX_MARGIN
        rect = QRect(x, y, self.AVATAR_SIZE, self.AVATAR_SIZE)
        painter.drawPixmap(rect, self.avatar)

        # Draw username
        username_string = index.data(self.UsernameRole).toPyObject()
        username = QTextDocument()
        username.setHtml("%s" % username_string)
        username.setDefaultFont(USERNAME_FONT)
        #username.setTextWidth(self.__calculate_text_width(width))

        x = option.rect.left() + self.BOX_MARGIN + self.AVATAR_SIZE
        y = option.rect.top() + self.BOX_MARGIN
        painter.translate(x, y)
        if selected:
            painter.setPen(option.palette.highlightedText().color())
        username.drawContents(painter)

        # Draw protocol
        y = username.size().height() + self.TEXT_MARGIN
        painter.translate(0, y)
        protocol_string = index.data(self.ProtocolRole).toPyObject()
        protocol = QTextDocument()
        protocol.setHtml("<span style='color: #%s;'>%s</span>" % (protocol_color, protocol_string))
        protocol.setDefaultFont(PROTOCOL_FONT)
        protocol.drawContents(painter)

        painter.restore()

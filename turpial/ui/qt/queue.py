# -*- coding: utf-8 -*-

# Qt status queue for Turpial

#import os
#import sys
#
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFont
#from PyQt4.QtGui import QMenu
#from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QWidget
#from PyQt4.QtGui import QAction
#from PyQt4.QtGui import QPixmap
#from PyQt4.QtGui import QDialog
#from PyQt4.QtGui import QListView
from PyQt4.QtGui import QTableView
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
#from PyQt4.QtGui import QSizePolicy
#from PyQt4.QtGui import QTextDocument
#from PyQt4.QtGui import QStandardItem
#from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QStandardItemModel
#from PyQt4.QtGui import QStyledItemDelegate
#
from PyQt4.QtCore import Qt
#from PyQt4.QtCore import QSize
#from PyQt4.QtCore import QRect

from turpial.ui.lang import i18n
#from turpial.ui.qt.oauth import OAuthDialog
#from turpial.ui.qt.dialog import ModalDialog

#from libturpial.api.models.account import Account
from libturpial.common.tools import get_protocol_from, get_username_from

USERNAME_FONT = QFont("Helvetica", 14)
PROTOCOL_FONT = QFont("Helvetica", 11)

class QueueDialog(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('status_queue'))
        self.setFixedSize(500, 400)

        #self.list_ = QListView()
        #self.list_.setResizeMode(QListView.Adjust)
        #self.list_.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        #account_delegate = AccountDelegate(base)
        #self.list_.setItemDelegate(account_delegate)
        #self.list_.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.list_.clicked.connect(self.__account_clicked)
        self.list_ = QTableView()

        self.delete_button = QPushButton(i18n.get('delete'))
        self.delete_button.setEnabled(False)
        self.delete_button.setToolTip(i18n.get('delete_selected_message'))
        self.delete_button.clicked.connect(self.__delete_message)

        self.clear_button = QPushButton(i18n.get('delete_all'))
        self.clear_button.setEnabled(False)
        self.clear_button.setToolTip(i18n.get('delete_all_messages_in_queue'))
        self.clear_button.clicked.connect(self.__delete_all)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(self.clear_button)
        button_box.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.list_, 1)
        layout.addLayout(button_box)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 0)
        self.setLayout(layout)

        self.__update()

        #self.base.account_deleted.connect(self.__update)
        #self.base.account_loaded.connect(self.__update)
        #self.base.account_registered.connect(self.__update)

    def __update(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderItem(0, QStandardItem(i18n.get('account')))
        model.setHorizontalHeaderItem(1, QStandardItem(i18n.get('message')))
        self.list_.resizeColumnToContents(1)
        self.list_.setModel(model)
        row = 0
        for status in self.base.core.list_queue():
            username = get_username_from(status.account_id)
            protocol_image = "%s.png" % get_protocol_from(status.account_id)
            item = QStandardItem(username)
            item.setIcon(QIcon(self.base.load_image(protocol_image, True)))
            model.setItem(row, 0, item)
            model.setItem(row, 1, QStandardItem(status.text))
            row += 1
        #accounts = self.base.core.get_registered_accounts()
        #count = 0
        #for account in accounts:
        #    item = QStandardItem()
        #    filepath = os.path.join(self.base.images_path, 'unknown.png')
        #    item.setData(filepath, AccountDelegate.AvatarRole)
        #    item.setData(get_username_from(account.id_), AccountDelegate.UsernameRole)
        #    item.setData(get_protocol_from(account.id_).capitalize(), AccountDelegate.ProtocolRole)
        #    item.setData(account.id_, AccountDelegate.IdRole)
        #    model.appendRow(item)
        #    count += 1

        self.__enable(True)
        self.delete_button.setEnabled(False)
        self.clear_button.setEnabled(False)

    def __account_clicked(self, point):
        self.delete_button.setEnabled(True)
        self.clear_button.setEnabled(True)

    def __delete_message(self):
        self.__enable(False)
        selection = self.list_.selectionModel()
        index = selection.selectedIndexes()[0]
        account_id = str(index.data(AccountDelegate.IdRole).toPyObject())
        message = i18n.get('delete_account_confirm') % account_id
        confirmation = self.base.show_confirmation_message(i18n.get('confirm_delete'),
            message)
        if not confirmation:
            self.__enable(True)
            return
        self.base.delete_account(account_id)

    def __delete_all(self):
        self.__enable(False)
        selection = self.list_.selectionModel()
        index = selection.selectedIndexes()[0]
        account_id = str(index.data(AccountDelegate.IdRole).toPyObject())
        self.base.load_account(account_id)

    def __enable(self, value):
        # TODO: Display a loading message/indicator
        self.list_.setEnabled(value)
        self.delete_button.setEnabled(value)
        self.clear_button.setEnabled(value)

#class AccountDelegate(QStyledItemDelegate):
#    UsernameRole = Qt.UserRole + 100
#    ProtocolRole = Qt.UserRole + 101
#    AvatarRole = Qt.UserRole + 102
#    IdRole = Qt.UserRole + 103
#
#    AVATAR_SIZE = 48
#    BOX_MARGIN = 4
#    TEXT_MARGIN = 0
#
#    def __init__(self, base):
#        QStyledItemDelegate.__init__(self)
#        self.avatar = None
#
#    def sizeHint(self, option, index):
#        height = self.AVATAR_SIZE + (self.BOX_MARGIN * 2)
#        self.size = QSize(option.rect.width(), height)
#        return self.size
#
#    def paint(self, painter, option, index):
#        painter.save()
#
#        selected = False
#        cell_width = self.size.width()
#
#        rect = option.rect
#        rect.width = self.size.width()
#        rect.height = self.size.height()
#        protocol_color = "999"
#        if option.state & QStyle.State_Selected:
#            painter.fillRect(rect, option.palette.highlight())
#            protocol_color = "ddd"
#            selected = True
#
#        # Draw avatar
#        if not self.avatar:
#            avatar_filepath = index.data(self.AvatarRole).toPyObject()
#            self.avatar = QPixmap(avatar_filepath)
#        x = option.rect.left() + self.BOX_MARGIN
#        y = option.rect.top() + self.BOX_MARGIN
#        rect = QRect(x, y, self.AVATAR_SIZE, self.AVATAR_SIZE)
#        painter.drawPixmap(rect, self.avatar)
#
#        # Draw username
#        username_string = index.data(self.UsernameRole).toPyObject()
#        username = QTextDocument()
#        username.setHtml("%s" % username_string)
#        username.setDefaultFont(USERNAME_FONT)
#        #username.setTextWidth(self.__calculate_text_width(width))
#
#        x = option.rect.left() + self.BOX_MARGIN + self.AVATAR_SIZE
#        y = option.rect.top() + self.BOX_MARGIN
#        painter.translate(x, y)
#        if selected:
#            painter.setPen(option.palette.highlightedText().color())
#        username.drawContents(painter)
#
#        # Draw protocol
#        y = username.size().height() + self.TEXT_MARGIN
#        painter.translate(0, y)
#        protocol_string = index.data(self.ProtocolRole).toPyObject()
#        protocol = QTextDocument()
#        protocol.setHtml("<span style='color: #%s;'>%s</span>" % (protocol_color, protocol_string))
#        protocol.setDefaultFont(PROTOCOL_FONT)
#        protocol.drawContents(painter)
#
#        painter.restore()

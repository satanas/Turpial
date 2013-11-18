# -*- coding: utf-8 -*-

# Qt account manager for Turpial

import os
import sys

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtGui import QStyledItemDelegate
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QTimer

from turpial.ui.lang import i18n
from turpial.ui.qt.oauth import OAuthDialog
from turpial.ui.qt.widgets import ModalDialog, ErrorLabel

from libturpial.api.models.account import Account
from libturpial.common.tools import get_protocol_from, get_username_from

USERNAME_FONT = QFont("Helvetica", 14)
PROTOCOL_FONT = QFont("Helvetica", 11)

class AccountsDialog(ModalDialog):
    def __init__(self, base):
        ModalDialog.__init__(self, 380,325)
        self.base = base
        self.setWindowTitle(i18n.get('accounts'))

        self.list_ = QListView()
        self.list_.setResizeMode(QListView.Adjust)
        self.list_.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        account_delegate = AccountDelegate(base)
        self.list_.setItemDelegate(account_delegate)
        self.list_.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_.clicked.connect(self.__account_clicked)

        twitter_menu = QAction(i18n.get('twitter'), self)
        twitter_menu.setIcon(QIcon(base.load_image('twitter.png', True)))
        twitter_menu.setToolTip(i18n.get('register_a_twitter_account'))
        twitter_menu.triggered.connect(self.__register_twitter_account)

        # TODO: Enable when identi.ca support is ready
        identica_menu = QAction(i18n.get('identica'), self)
        identica_menu.setIcon(QIcon(base.load_image('identica.png', True)))
        identica_menu.setToolTip(i18n.get('register_an_identica_account'))
        identica_menu.setEnabled(False)

        self.menu = QMenu()
        self.menu.addAction(twitter_menu)
        self.menu.addAction(identica_menu)

        self.new_button = QPushButton(i18n.get('new'))
        self.new_button.setMenu(self.menu)
        self.new_button.setToolTip(i18n.get('register_a_new_account'))

        self.delete_button = QPushButton(i18n.get('delete'))
        self.delete_button.setEnabled(False)
        self.delete_button.setToolTip(i18n.get('delete_an_existing_account'))
        self.delete_button.clicked.connect(self.__delete_account)

        self.relogin_button = QPushButton(i18n.get('relogin'))
        self.relogin_button.setEnabled(False)
        self.relogin_button.setToolTip(i18n.get('relogin_this_account'))
        self.relogin_button.clicked.connect(self.__relogin_account)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.setSpacing(4)
        button_box.addWidget(self.new_button)
        button_box.addWidget(self.delete_button)
        button_box.addWidget(self.relogin_button)

        self.error_message = ErrorLabel()
        self.error_message.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(self.list_)
        layout.addWidget(self.error_message)
        layout.addLayout(button_box)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        self.__update()

        self.base.account_deleted.connect(self.__update)
        self.base.account_loaded.connect(self.__update)
        self.base.account_registered.connect(self.__update)

        self.exec_()

    def __update(self):
        model = QStandardItemModel()
        self.list_.setModel(model)
        accounts = self.base.core.get_registered_accounts()
        count = 0
        for account in accounts:
            item = QStandardItem()
            filepath = os.path.join(self.base.images_path, 'unknown.png')
            item.setData(filepath, AccountDelegate.AvatarRole)
            item.setData(get_username_from(account.id_), AccountDelegate.UsernameRole)
            item.setData(get_protocol_from(account.id_).capitalize(), AccountDelegate.ProtocolRole)
            item.setData(account.id_, AccountDelegate.IdRole)
            model.appendRow(item)
            count += 1

        self.__enable(True)
        self.delete_button.setEnabled(False)
        self.relogin_button.setEnabled(False)

    def __account_clicked(self, point):
        self.delete_button.setEnabled(True)
        self.relogin_button.setEnabled(True)

    def __delete_account(self):
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

    def __register_twitter_account(self):
        self.__enable(False)
        account = Account.new('twitter')
        try:
            oauth_dialog = OAuthDialog(self, account.request_oauth_access())
        except Exception, e:
            err_msg = "%s: %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print err_msg
            self.error(i18n.get('problems_registering_new_account'))
            self.__enable(True)
            return

        if oauth_dialog.result() == QDialog.Accepted:
            pin = oauth_dialog.pin.text()
            try:
                account.authorize_oauth_access(pin)
                self.base.save_account(account)
            except Exception, e:
                err_msg = "%s: %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print err_msg
                self.error(i18n.get('problems_registering_new_account'))
                self.__enable(True)

    def __relogin_account(self):
        self.__enable(False)
        selection = self.list_.selectionModel()
        index = selection.selectedIndexes()[0]
        account_id = str(index.data(AccountDelegate.IdRole).toPyObject())
        self.base.load_account(account_id)

    def __enable(self, value):
        # TODO: Display a loading message/indicator
        self.list_.setEnabled(value)
        self.new_button.setEnabled(value)
        self.delete_button.setEnabled(value)
        self.relogin_button.setEnabled(value)

    def __on_timeout(self):
        self.error_message.setText('')
        self.error_message.setVisible(False)

    def error(self, message):
        self.error_message.setText(message)
        self.error_message.setVisible(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.__on_timeout)
        self.timer.start(5000)

class AccountDelegate(QStyledItemDelegate):
    UsernameRole = Qt.UserRole + 100
    ProtocolRole = Qt.UserRole + 101
    AvatarRole = Qt.UserRole + 102
    IdRole = Qt.UserRole + 103

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

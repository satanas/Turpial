# -*- coding: utf-8 -*-

# Qt widget to implement statuses column in Turpial

import os

#from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QLine
from PyQt4.QtCore import QString

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtGui import QStyledItemDelegate
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton
from turpial.ui.qt.loader import BarLoadIndicator

from libturpial.common.tools import get_account_id_from, get_column_slug_from, get_protocol_from,\
        get_username_from

FULLNAME_FONT = QFont("Helvetica", 13)
USERNAME_FONT = QFont("Helvetica", 11)
FOOTER_FONT = QFont("Helvetica", 11)


class StatusesColumn(QWidget):
    def __init__(self, base, column_id):
        QWidget.__init__(self)
        self.base = base
        self.setMinimumWidth(280)
        self.column_id = column_id
        #self.updating = False

        account_id = get_account_id_from(column_id)
        username = get_username_from(account_id)
        column_slug = get_column_slug_from(column_id)
        protocol_id = get_protocol_from(account_id)

        icon = QLabel()
        protocol_img = "%s.png" % protocol_id
        icon.setPixmap(base.load_image(protocol_img, True))

        label = "%s :: %s" % (username, column_slug)
        caption = QLabel(label)

        close_button = ImageButton(base, 'action-delete.png',
                i18n.get('delete_column'))
        close_button.clicked.connect(self.__delete_column)

        header = QHBoxLayout()
        header.addWidget(icon)
        header.addWidget(caption, 1)
        header.addWidget(close_button)

        self.loader = BarLoadIndicator()
        self.loader.setVisible(False)

        self.list_ = QListView()
        self.list_.setResizeMode(QListView.Adjust)
        self.list_.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.list_.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self.loader)
        layout.addWidget(self.list_)

        self.setLayout(layout)

        model = QStandardItemModel()
        self.list_.setModel(model)

        status_delegate = StatusDelegate(base)
        self.list_.setItemDelegate(status_delegate)

    def __delete_column(self):
        self.base.core.delete_column(self.column_id)

    def start_updating(self):
        self.loader.setVisible(True)

    def stop_updating(self):
        self.loader.setVisible(False)

    def update_statuses(self, statuses):
        model = self.list_.model()
        for status in statuses:
            filepath = os.path.join(self.base.images_path, 'unknown.png')
            timestamp = self.base.humanize_timestamp(status.timestamp)
            if status.repeated_by:
                repeated_by = "%s %s" % (i18n.get('retweeted_by'), status.repeated_by)
            else:
                repeated_by = None

            item = QStandardItem()
            item.setData(status.text, StatusDelegate.MessageRole)
            item.setData(filepath, StatusDelegate.AvatarRole)
            item.setData('', StatusDelegate.UsernameRole)
            item.setData(status.username, StatusDelegate.FullnameRole)
            item.setData(repeated_by, StatusDelegate.RepostedRole)
            item.setData(status.protected, StatusDelegate.ProtectedRole)
            item.setData(status.verified, StatusDelegate.VerifiedRole)
            item.setData(status.favorited, StatusDelegate.FavoritedRole)
            item.setData(status.repeated, StatusDelegate.RepeatedRole)
            item.setData(timestamp, StatusDelegate.DateRole)
            model.appendRow(item)


class StatusDelegate(QStyledItemDelegate):
    FullnameRole = Qt.UserRole + 100
    UsernameRole = Qt.UserRole + 101
    AvatarRole = Qt.UserRole + 102
    MessageRole = Qt.UserRole + 103
    DateRole = Qt.UserRole + 104
    RepostedRole = Qt.UserRole + 105
    ProtectedRole = Qt.UserRole + 106
    FavoritedRole = Qt.UserRole + 107
    RepeatedRole = Qt.UserRole + 108
    VerifiedRole = Qt.UserRole + 109

    AVATAR_SIZE = 48
    BOX_MARGIN = 2
    LEFT_MESSAGE_MARGIN = 8
    TOP_MESSAGE_MARGIN = 0
    BOTTOM_MESSAGE_MARGIN = 0
    COMPLEMENT_HEIGHT = 5

    def __init__(self, base):
        QStyledItemDelegate.__init__(self)
        self.favorite_icon = base.load_image('mark-favorite.png', True)
        self.verified_icon = base.load_image('mark-verified.png', True)
        self.protected_icon = base.load_image('mark-protected.png', True)
        self.repeated_icon = base.load_image('mark-repeated.png', True)
        self.reposted_icon = base.load_image('mark-reposted.png', True)
        self.avatar = None

    def __calculate_text_width(self, width):
        width -= ((self.BOX_MARGIN * 2) + self.AVATAR_SIZE + self.LEFT_MESSAGE_MARGIN)
        return width

    def __render_fullname(self, width, index):
        fullname = index.data(self.FullnameRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml("<b>%s</b>" % fullname)
        doc.setDefaultFont(FULLNAME_FONT)
        doc.setTextWidth(self.__calculate_text_width(width))
        return doc

    def __render_status_message(self, width, index):
        message = index.data(self.MessageRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml(message)
        doc.setTextWidth(self.__calculate_text_width(width))
        return doc

    def __render_username(self, width, index):
        username_string = index.data(self.UsernameRole).toPyObject()
        username = QTextDocument()
        if username_string != '':
            username.setHtml("<span style='color: #666;'>@%s</span>" % username_string)
        else:
            username.setHtml("<span style='color: #666;'></span>" % username_string)
        username.setDefaultFont(USERNAME_FONT)
        username.setTextWidth(self.__calculate_text_width(width))
        return username

    def sizeHint(self, option, index):
        fullname = self.__render_fullname(option.rect.size().width(), index)
        message = self.__render_status_message(option.rect.size().width(), index)

        height = option.rect.top() + fullname.size().height() + self.TOP_MESSAGE_MARGIN + message.size().height()
        if height < self.AVATAR_SIZE:
            height = self.AVATAR_SIZE + self.COMPLEMENT_HEIGHT

        height += self.BOTTOM_MESSAGE_MARGIN + 16 + (self.BOX_MARGIN * 3)

        self.size = QSize(option.rect.width(), height)
        return self.size

    def paint(self, painter, option, index):
        painter.save()

        cell_width = self.size.width()

        #if option.state & QStyle.State_Selected:
        #    painter.fillRect(option.rect, option.palette.highlight())
        #painter.drawRect(option.rect)


        # Draw marks before translating painter
        # =====================================

        # Draw avatar
        if not self.avatar:
            avatar_filepath = index.data(self.AvatarRole).toPyObject()
            self.avatar = QPixmap(avatar_filepath)
        x = option.rect.left() + (self.BOX_MARGIN * 2)
        y = option.rect.top() + (self.BOX_MARGIN * 2)
        rect = QRect(x, y, self.AVATAR_SIZE, self.AVATAR_SIZE)
        painter.drawPixmap(rect, self.avatar)

        # Draw verified account icon
        if index.data(self.VerifiedRole).toPyObject():
            rect2 = QRect(rect.right() - 11, rect.bottom() - 10, 16, 16)
            painter.drawPixmap(rect2, self.verified_icon)

        marks_margin = 0
        # Favorite mark
        if index.data(self.FavoritedRole).toPyObject():
            x = cell_width - 16 - self.BOX_MARGIN
            y = option.rect.top() + self.BOX_MARGIN
            rect = QRect(x, y, 16, 16)
            painter.drawPixmap(rect, self.favorite_icon)
            marks_margin = 16

        # Draw reposted icon
        if index.data(self.RepeatedRole).toPyObject():
            x = cell_width - 16 - self.BOX_MARGIN - marks_margin
            y = option.rect.top() + self.BOX_MARGIN
            rect = QRect(x, y, 16, 16)
            painter.drawPixmap(rect, self.repeated_icon)

        # Draw protected account icon
        protected_icon_margin = 0
        if index.data(self.ProtectedRole).toPyObject():
            x = option.rect.left() + self.BOX_MARGIN + self.AVATAR_SIZE + self.LEFT_MESSAGE_MARGIN
            y = option.rect.top() + self.BOX_MARGIN
            rect = QRect(x, y, 16, 16)
            painter.drawPixmap(rect, self.protected_icon)
            protected_icon_margin = 16

        # ==== End of pixmap drawing ====

        accumulated_height = 0

        # Draw fullname
        fullname = self.__render_fullname(cell_width, index)
        x = option.rect.left() + self.BOX_MARGIN + self.AVATAR_SIZE
        x += self.LEFT_MESSAGE_MARGIN + protected_icon_margin
        y = option.rect.top()
        painter.translate(x, y)
        fullname.drawContents(painter)

        # Draw username
        username = self.__render_username(cell_width, index)
        painter.translate(fullname.idealWidth(), 0)
        username.drawContents(painter)

        # Draw status message
        x = -fullname.idealWidth() - protected_icon_margin
        y = fullname.size().height() + self.TOP_MESSAGE_MARGIN
        painter.translate(x, y)
        message = self.__render_status_message(cell_width, index)
        message.drawContents(painter)
        accumulated_height += y + message.size().height()

        # Draw reposted by
        x = self.BOX_MARGIN + 16 - (self.LEFT_MESSAGE_MARGIN + self.AVATAR_SIZE)
        y = message.size().height() + self.BOTTOM_MESSAGE_MARGIN
        if accumulated_height < self.AVATAR_SIZE:
            y += (self.AVATAR_SIZE - accumulated_height) + self.COMPLEMENT_HEIGHT
        painter.translate(x, y)

        reposted_by = index.data(self.RepostedRole).toPyObject()
        if reposted_by:
            reposted = QTextDocument()
            reposted.setHtml("<span style='color: #999;'>%s</span>" % reposted_by)
            reposted.setDefaultFont(FOOTER_FONT)
            reposted.setTextWidth(self.__calculate_text_width(cell_width))
            reposted.drawContents(painter)

            # Draw reposted icon
            rect2 = QRect(-16, 3, 16, 16)
            painter.drawPixmap(rect2, self.reposted_icon)

        # Draw datetime
        datetime = index.data(self.DateRole).toPyObject()
        timestamp = QTextDocument()
        timestamp.setHtml("<span style='color: #999;'>%s</span>" % datetime)
        timestamp.setDefaultFont(FOOTER_FONT)
        timestamp.setTextWidth(self.__calculate_text_width(cell_width))
        x = self.size.width() - timestamp.idealWidth() - 20 - self.BOX_MARGIN
        painter.translate(x, 0)
        timestamp.drawContents(painter)

        painter.resetTransform()
        painter.translate(0, option.rect.bottom())
        line = QLine(0, 0, option.rect.width(), 0)
        painter.setPen(QColor(230, 230, 230))
        painter.drawLine(line)

        painter.restore()

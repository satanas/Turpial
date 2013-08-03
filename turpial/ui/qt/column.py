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
from PyQt4.QtGui import QProgressBar
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtGui import QStyledItemDelegate
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton

FULLNAME_FONT = QFont("Helvetica", 13)
USERNAME_FONT = QFont("Helvetica", 11)
FOOTER_FONT = QFont("Helvetica", 11)


class StatusesColumn(QWidget):
    def __init__(self, base, test=False):
        QWidget.__init__(self)
        self.base = base
        self.setMinimumWidth(280)

        icon = QLabel()
        icon.setPixmap(base.load_image('twitter.png', True))

        caption = QLabel('satanas82 :: timeline')

        close_button = ImageButton(base, 'action-delete.png',
                i18n.get('delete_column'))

        header = QHBoxLayout()
        header.addWidget(icon)
        header.addWidget(caption, 1)
        header.addWidget(close_button)

        self.loader = QProgressBar()
        self.loader.setMinimum(0)
        self.loader.setMaximum(0)
        self.loader.setMaximumHeight(6)
        self.loader.setTextVisible(False)

        self._list = QListView()

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self.loader)
        layout.addWidget(self._list)

        self.setLayout(layout)

        model = QStandardItemModel()
        self._list.setModel(model)

        status_delegate = StatusDelegate(base)
        self._list.setItemDelegate(status_delegate)
        self._list.setResizeMode(QListView.Adjust)

        item = QStandardItem()
        item.setData("Now that we know who you are, I know who I am. I'm not a mistake! It all makes sense! In a comic, you know how you can tell who the arch-villain's going to be?", StatusDelegate.MessageRole)
        filepath = os.path.join(self.base.images_path, 'unknown.png')
        item.setData(filepath, StatusDelegate.AvatarRole)
        item.setData("satanas82", StatusDelegate.UsernameRole)
        item.setData("Wil Alvarez", StatusDelegate.FullnameRole)
        item.setData(None, StatusDelegate.RepostedRole)
        item.setData(True, StatusDelegate.ProtectedRole)
        item.setData(True, StatusDelegate.FavoritedRole)
        item.setData(False, StatusDelegate.RepeatedRole)

        item2 = QStandardItem()
        item2.setData("The path of the righteous man is beset on all sides by the iniquities of the selfish and the tyranny of evil men", StatusDelegate.MessageRole)
        item2.setData(filepath, StatusDelegate.AvatarRole)
        item2.setData("TurpialVe", StatusDelegate.UsernameRole)
        item2.setData("Turpial", StatusDelegate.FullnameRole)
        item2.setData("Reposted by mengano", StatusDelegate.RepostedRole)
        item2.setData(False, StatusDelegate.ProtectedRole)
        item2.setData(False, StatusDelegate.FavoritedRole)
        item2.setData(True, StatusDelegate.RepeatedRole)

        if test:
            model.appendRow(item)
            model.appendRow(item2)


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

    AVATAR_SIZE = 48
    BOX_MARGIN = 2
    LEFT_MESSAGE_MARGIN = 8
    TOP_MESSAGE_MARGIN = 0
    BOTTOM_MESSAGE_MARGIN = 0

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
        username.setHtml("<span style='color: #666;'>@%s</span>" % username_string)
        username.setDefaultFont(USERNAME_FONT)
        username.setTextWidth(self.__calculate_text_width(width))
        return username

    def sizeHint(self, option, index):
        fullname = self.__render_fullname(option.rect.size().width(), index)
        message = self.__render_status_message(option.rect.size().width(), index)

        height = fullname.size().height() + self.TOP_MESSAGE_MARGIN
        height += message.size().height() + self.BOTTOM_MESSAGE_MARGIN + 16 + (self.BOX_MARGIN * 3)

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
        rect2 = QRect(rect.right() - 11, rect.bottom() - 10, 16, 16)
        painter.drawPixmap(rect2, self.verified_icon)

        marks_margin = 0
        # Favorite mark
        if index.data(self.FavoritedRole).toPyObject():
            x = cell_width - 8 - self.BOX_MARGIN
            y = option.rect.top() + self.BOX_MARGIN
            rect = QRect(x, y, 16, 16)
            painter.drawPixmap(rect, self.favorite_icon)
            marks_margin = 16

        # Draw reposted icon
        if index.data(self.RepeatedRole).toPyObject():
            x = cell_width -8 - self.BOX_MARGIN - marks_margin
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

        # Draw reposted by
        x = self.BOX_MARGIN + 16 - (self.LEFT_MESSAGE_MARGIN + self.AVATAR_SIZE)
        y = message.size().height() + self.BOTTOM_MESSAGE_MARGIN
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
        datetime = "1s"
        timestamp = QTextDocument()
        timestamp.setHtml("<span style='color: #999;'>%s</span>" % datetime)
        timestamp.setDefaultFont(FOOTER_FONT)
        timestamp.setTextWidth(self.__calculate_text_width(cell_width))
        x = self.size.width() - timestamp.idealWidth() - 15 - self.BOX_MARGIN
        painter.translate(x, 0)
        timestamp.drawContents(painter)

        painter.resetTransform()
        painter.translate(0, option.rect.bottom())
        line = QLine(0, 0, option.rect.width(), 0)
        painter.setPen(QColor(230, 230, 230))
        painter.drawLine(line)

        painter.restore()

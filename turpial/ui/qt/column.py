# -*- coding: utf-8 -*-

# Qt widget to implement statuses column in Turpial

import os

#from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QRectF
from PyQt4.QtCore import QLine
from PyQt4.QtCore import QString

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QFont
from PyQt4.QtGui import QFontDatabase
from PyQt4.QtGui import QStyle
from PyQt4.QtGui import QAbstractTextDocumentLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QStyledItemDelegate
from PyQt4.QtGui import QProgressBar
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton

AVATAR_SIZE = 48
#FULLNAME_FONT = QFont("Aaargh", 15)
#FULLNAME_FONT = QFont("CicleGordita", 14)
#USERNAME_FONT = QFont("Helvetica", 12)
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
        item.setData("1375478790", StatusDelegate.DateRole)

        item2 = QStandardItem()
        item2.setData("The path of the righteous man is beset on all sides by the iniquities of the selfish and the tyranny of evil men", StatusDelegate.MessageRole)
        item2.setData(filepath, StatusDelegate.AvatarRole)
        item2.setData("TurpialVe", StatusDelegate.UsernameRole)
        item2.setData("Turpial", StatusDelegate.FullnameRole)
        item2.setData("1375478800", StatusDelegate.DateRole)

        if test:
            model.appendRow(item)
            model.appendRow(item2)


class StatusDelegate(QStyledItemDelegate):
    FullnameRole = Qt.UserRole + 100
    UsernameRole = Qt.UserRole + 101
    AvatarRole = Qt.UserRole + 102
    MessageRole = Qt.UserRole + 103
    DateRole = Qt.UserRole + 104

    AVATAR_SIZE = 48
    BOX_MARGIN = 2
    LEFT_MESSAGE_MARGIN = 10
    TOP_MESSAGE_MARGIN = 1
    BOTTOM_MESSAGE_MARGIN = 3

    def __init__(self, base):
        QStyledItemDelegate.__init__(self)
        self.base = base

    def __calculate_text_width(self, option):
        width = option.rect.width()
        width -= (self.BOX_MARGIN + self.AVATAR_SIZE + self.LEFT_MESSAGE_MARGIN)
        return width

    def __render_fullname(self, option, index):
        fullname = index.data(self.FullnameRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml("<b>%s</b>" % fullname)
        doc.setDefaultFont(FULLNAME_FONT)
        doc.setTextWidth(self.__calculate_text_width(option))
        return doc

    def __render_status_message(self, option, index):
        message = index.data(self.MessageRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml(message)
        doc.setTextWidth(self.__calculate_text_width(option))
        return doc


    def sizeHint(self, option, index):
        fullname = self.__render_fullname(option, index)
        message = self.__render_status_message(option, index)

        height = self.BOX_MARGIN + fullname.size().height() + self.TOP_MESSAGE_MARGIN
        height += message.size().height() + self.BOTTOM_MESSAGE_MARGIN + 16 + self.BOX_MARGIN

        width = self.BOX_MARGIN + self.AVATAR_SIZE + self.LEFT_MESSAGE_MARGIN
        width += message.idealWidth() + self.BOX_MARGIN
        return QSize(width, height)

    def paint(self, painter, option, index):
        current_width = 0
        painter.save()

        #if option.state & QStyle.State_Selected:
        #    painter.fillRect(option.rect, option.palette.highlight())
        #painter.drawRect(option.rect)

        # Draw avatar
        avatar_filepath = index.data(self.AvatarRole).toPyObject()
        avatar = QPixmap(avatar_filepath)
        x = option.rect.left() + self.BOX_MARGIN
        y = option.rect.top() + self.BOX_MARGIN
        rect = QRect(x, y, self.AVATAR_SIZE, self.AVATAR_SIZE)
        painter.drawPixmap(rect, avatar)

        # Draw verified account icon
        verified_icon = self.base.load_image('mark-verified.png', True)
        rect2 = QRect(rect.right() - 11, rect.bottom() - 10, 16, 16)
        painter.drawPixmap(rect2, verified_icon)

        # Draw protected account icon
        protected_icon = self.base.load_image('mark-protected.png', True)
        rect = QRect(rect.right() + self.LEFT_MESSAGE_MARGIN, y, 16, 16)
        painter.drawPixmap(rect, protected_icon)

        # Draw fullname
        fullname = self.__render_fullname(option, index)
        painter.translate(rect.right(), option.rect.top())
        fullname.drawContents(painter)

        # Draw username
        username = index.data(self.UsernameRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml("<span style='color: #666;'>@%s</span>" % username)
        doc.setDefaultFont(USERNAME_FONT)
        doc.setTextWidth(self.__calculate_text_width(option))
        painter.translate(fullname.idealWidth(), 0)
        doc.drawContents(painter)


        ## Draw favorite icon
        #favorite_icon = self.base.load_image('mark-favorite.png', True)
        #rect2 = QRect(option.rect.right() - 16, rect.top(), 16, 16)
        #painter.drawPixmap(rect2, favorite_icon)

        ## Draw reposted icon
        #reposted_icon = self.base.load_image('mark-repeated.png', True)
        #rect2 = QRect(option.rect.right() - 32, rect.top(), 16, 16)
        #painter.drawPixmap(rect2, reposted_icon)

        # Draw status message
        painter.resetTransform()
        message = self.__render_status_message(option, index)

        x = self.BOX_MARGIN + self.AVATAR_SIZE + self.LEFT_MESSAGE_MARGIN
        y = option.rect.top() + fullname.size().height() + self.TOP_MESSAGE_MARGIN
        painter.translate(x, y)
        message.drawContents(painter)

        ## Draw reposted by
        #reposted_by = "Reposted by fulano" #index.data(self.MessageRole).toPyObject()
        #doc = QTextDocument()
        #doc.setHtml("<span style='color: #999;'>%s</span>" % reposted_by)
        #doc.setDefaultFont(FOOTER_FONT)
        #doc.setTextWidth(self.__calculate_text_width(option.rect.width()))

        #painter.translate(-(self.AVATAR_SIZE + (self.LEFT_AVATAR_MARGIN * 2) - 16), height_offset)
        #doc.drawContents(painter)

        ## Draw reposted icon
        #reposted_icon = self.base.load_image('mark-reposted.png', True)
        #rect2 = QRect(-16, 3, 16, 16)
        #painter.drawPixmap(rect2, reposted_icon)

        # Draw datetime
        painter.resetTransform()
        datetime = "6 min"
        timestamp = QTextDocument()
        timestamp.setHtml("<span style='color: #999;'>%s</span>" % datetime)
        timestamp.setDefaultFont(FOOTER_FONT)
        timestamp.setTextWidth(self.__calculate_text_width(option))

        x = option.rect.right() - self.BOX_MARGIN - timestamp.idealWidth()
        y = option.rect.bottom() - 16 - self.BOX_MARGIN

        painter.translate(x, y)
        timestamp.drawContents(painter)

        #painter.translate(-w - 16, 20)
        #line = QLine(0, 0, option.rect.width(), 0)
        #painter.setPen(QColor(230, 230, 230))
        #painter.drawLine(line)

        painter.resetTransform()
        line = QLine(0, option.rect.bottom(), option.rect.width(), option.rect.bottom())
        painter.translate(option.rect.left(), option.rect.bottom() - 1)
        #line = QLine(0, 0, option.rect.width(), 0)
        painter.setPen(QColor(230, 230, 230))
        painter.drawLine(line)

        painter.restore()

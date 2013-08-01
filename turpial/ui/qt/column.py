# -*- coding: utf-8 -*-

# Qt widget to implement statuses column in Turpial

import os

#from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QString

from PyQt4.QtGui import QIcon
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
        self.setMinimumWidth(200)

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

        item2 = QStandardItem()
        item2.setData("The path of the righteous man is beset on all sides by the iniquities of the selfish and the tyranny of evil men", StatusDelegate.MessageRole)
        item2.setData(filepath, StatusDelegate.AvatarRole)
        item2.setData("TurpialVe", StatusDelegate.UsernameRole)
        item2.setData("Turpial", StatusDelegate.FullnameRole)

        if test:
            model.appendRow(item)
            model.appendRow(item2)


class StatusDelegate(QStyledItemDelegate):
    FullnameRole = Qt.UserRole + 100
    UsernameRole = Qt.UserRole + 101
    AvatarRole = Qt.UserRole + 102
    MessageRole = Qt.UserRole + 103
    DateRole = Qt.UserRole + 104

    AVATAR_MARGIN = 3

    def __init__(self, base):
        QStyledItemDelegate.__init__(self)
        self.base = base

    def __calculate_text_width(self, full_width):
        return full_width - (AVATAR_SIZE + (self.AVATAR_MARGIN * 2))

    def sizeHint(self, option, index):
        height = 0

        username = index.data(self.UsernameRole).toPyObject()
        doc = QTextDocument()
        doc.setDefaultFont(FULLNAME_FONT)
        doc.setHtml("%s" % username)
        doc.setTextWidth(self.__calculate_text_width(option.rect.width()))
        height += doc.size().height()

        #print "sizeHint after: %s" % option.rect
        message = index.data(self.MessageRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml(message)
        doc.setTextWidth(self.__calculate_text_width(option.rect.width()))
        #doc.adjustSize()
        height += doc.size().height()
        #print "sizeHint before: %s" % QSize(doc.idealWidth(), doc.size().height())
        #print "size %s, %s, %s" % (self.__calculate_text_width(option.rect.width()), doc.idealWidth(), doc.size())
        #print height
        return QSize(doc.idealWidth(), height + 20)

    def paint(self, painter, option, index):
        current_width = 0
        painter.save()

        #if option.state & QStyle.State_Selected:
        #    painter.fillRect(option.rect, option.palette.highlight())
        #painter.drawRect(option.rect)

        # Draw avatar
        avatar_filepath = index.data(self.AvatarRole).toPyObject()
        avatar = QPixmap(avatar_filepath)
        rect = QRect(option.rect.left() + self.AVATAR_MARGIN,
                option.rect.top() + self.AVATAR_MARGIN, AVATAR_SIZE, AVATAR_SIZE)
        painter.drawPixmap(rect, avatar)

        # Draw verified account icon
        verified_icon = self.base.load_image('mark-verified.png', True)
        rect = QRect(rect.right() + 2, rect.top(), 16, 16)
        painter.drawPixmap(rect, verified_icon)

        # Draw protected account icon
        protected_icon = self.base.load_image('mark-protected.png', True)
        rect = QRect(rect.right(), rect.top(), 16, 16)
        painter.drawPixmap(rect, protected_icon)

        # Draw favorite icon
        favorite_icon = self.base.load_image('mark-favorite.png', True)
        rect2 = QRect(option.rect.right() - 16, rect.top(), 16, 16)
        painter.drawPixmap(rect2, favorite_icon)

        # Draw reposted icon
        reposted_icon = self.base.load_image('mark-reposted.png', True)
        rect2 = QRect(option.rect.right() - 32, rect.top(), 16, 16)
        painter.drawPixmap(rect2, reposted_icon)

        # Draw fullname
        fullname = index.data(self.FullnameRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml("%s" % fullname)
        font = QFont()
        font.setPointSize(14)
        doc.setDefaultFont(font)
        doc.setTextWidth(self.__calculate_text_width(option.rect.width()))

        painter.translate(rect.right(), option.rect.top())
        doc.drawContents(painter)
        fullname_width = doc.idealWidth()
        current_width += rect.right()

        # Draw username
        username = index.data(self.UsernameRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml("@%s" % username)
        doc.setDefaultFont(USERNAME_FONT)
        doc.setTextWidth(self.__calculate_text_width(option.rect.width()))
        painter.translate(fullname_width, 0)
        doc.drawContents(painter)
        current_width += fullname_width

        # Draw status message
        #date = index.data(DateRole)
        message = index.data(self.MessageRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml(message)
        doc.setTextWidth(self.__calculate_text_width(option.rect.width()))

        current_width -= AVATAR_SIZE + (self.AVATAR_MARGIN * 2)
        painter.translate(-current_width, 16)
        doc.drawContents(painter)
        height_offset = doc.size().height()

        # Draw reposted by
        reposted_by = "Reposted by fulano" #index.data(self.MessageRole).toPyObject()
        doc = QTextDocument()
        doc.setHtml(reposted_by)
        doc.setDefaultFont(FOOTER_FONT)
        doc.setTextWidth(self.__calculate_text_width(option.rect.width()))
        painter.translate(-(AVATAR_SIZE + (self.AVATAR_MARGIN * 2) - 16), height_offset)
        doc.drawContents(painter)

        # Draw reposted icon
        reposted_icon = self.base.load_image('mark-reposted.png', True)
        rect2 = QRect(-16, 0, 16, 16)
        painter.drawPixmap(rect2, reposted_icon)

        # Draw datetime
        datetime = "6 min ago"
        doc = QTextDocument()
        doc.setHtml("<span style='color: #666;font-family: \"Ropa Sans\", sans-serif;'>" + datetime + "</span><link href='http://fonts.googleapis.com/css?family=Ropa+Sans' rel='stylesheet' type='text/css'>")
        doc.setDefaultFont(FOOTER_FONT)
        doc.setTextWidth(self.__calculate_text_width(option.rect.width()))
        w = option.rect.right() - doc.idealWidth() - 15
        painter.translate(w, 0)
        doc.drawContents(painter)

        painter.restore()

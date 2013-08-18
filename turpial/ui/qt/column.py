# -*- coding: utf-8 -*-

# Qt widget to implement statuses column in Turpial

import os

from jinja2 import Template

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

from PyQt4.QtWebKit import QWebView
from PyQt4.QtWebKit import QWebPage

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton
from turpial.ui.qt.loader import BarLoadIndicator

from libturpial.common.tools import get_account_id_from, get_column_slug_from, get_protocol_from,\
        get_username_from

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

        self.list_ = QWebView()
        self.list_.linkClicked.connect(self.__link_clicked)
        page = self.list_.page()
        page.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.list_.setPage(page)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(header)
        layout.addWidget(self.loader)
        layout.addWidget(self.list_)

        self.setLayout(layout)

        self.stylesheet = self.__load_stylesheet()


    def __delete_column(self):
        self.base.core.delete_column(self.column_id)

    def __load_template(self, name):
        path = os.path.join(self.base.templates_path, name)
        fd = open(path)
        content = fd.read()
        fd.close()
        return Template(content)

    def __load_stylesheet(self):
        attrs = {
            'mark_protected': os.path.join(self.base.images_path, 'mark-protected.png'),
            'mark_favorited': os.path.join(self.base.images_path, 'mark-favorited2.png'),
            'mark_repeated': os.path.join(self.base.images_path, 'mark-repeated2.png'),
            'mark_reposted': os.path.join(self.base.images_path, 'mark-reposted.png'),
            'mark_verified': os.path.join(self.base.images_path, 'mark-verified.png'),
            'action_reply': os.path.join(self.base.images_path, 'action-reply.png'),
            'action_repeat': os.path.join(self.base.images_path, 'action-repeat.png'),
            'action_quote': os.path.join(self.base.images_path, 'action-quote.png'),
            'action_favorite': os.path.join(self.base.images_path, 'action-favorite.png'),
            'action_reply_shadowed': os.path.join(self.base.images_path, 'action-reply-shadowed.png'),
            'action_repeat_shadowed': os.path.join(self.base.images_path, 'action-repeat-shadowed.png'),
            'action_quote_shadowed': os.path.join(self.base.images_path, 'action-quote-shadowed.png'),
            'action_favorite_shadowed': os.path.join(self.base.images_path, 'action-favorite-shadowed.png'),
        }
        stylesheet = self.__load_template('style.css')
        return stylesheet.render(attrs)

    def __link_clicked(self, qurl):
        url = str(qurl.toString())
        if url.startswith('http'):
            self.base.open_url(url)
        elif url.startswith('hashtag'):
            account_id = url.split(':')[1]
            hashtag = "#%s" % url.split(':')[2]
            self.base.add_search_column(account_id, hashtag)
        elif url.startswith('cmd'):
            print url

    def start_updating(self):
        self.loader.setVisible(True)

    def stop_updating(self):
        self.loader.setVisible(False)

    def update_statuses(self, statuses):
        content = ""
        status_template = self.__load_template('status.html')
        for status in statuses:
            repeated_by = None
            in_reply_to = None
            message = status.text
            timestamp = self.base.humanize_timestamp(status.timestamp)

            if status.entities:
                # Highlight URLs
                for url in status.entities['urls']:
                    pretty_url = "<a href='%s'>%s</a>" % (url.url, url.display_text)
                    message = message.replace(url.search_for, pretty_url)
                # Highlight hashtags
                for hashtag in status.entities['hashtags']:
                    pretty_hashtag = "<a href='hashtag:%s:%s'>%s</a>" % (hashtag.account_id,
                            hashtag.display_text[1:], hashtag.display_text)
                    message = message.replace(hashtag.search_for, pretty_hashtag)
                # Highlight mentions
                for mention in status.entities['mentions']:
                    pretty_mention = "<a href='profile:%s'>%s</a>" % (mention.url, mention.display_text)
                    message = message.replace(mention.search_for, pretty_mention)

            if status.repeated_by:
                repeated_by = "%s %s" % (i18n.get('retweeted_by'), status.repeated_by)
            if status.in_reply_to_id:
                in_reply_to = "%s %s" % (i18n.get('in_reply_to'), status.in_reply_to_user)

            attrs = {'status': status, 'message': message, 'repeated_by': repeated_by,
                    'timestamp': timestamp, 'in_reply_to': in_reply_to, 'reply': i18n.get('reply'),
                    'quote': i18n.get('quote'), 'retweet': i18n.get('retweet'),
                    'mark_as_favorite': i18n.get('mark_as_favorite'),}

            content += status_template.render(attrs)

        html = self.__load_template('column.html')
        args = {'stylesheet': self.stylesheet, 'content': content}
        page = html.render(args)

        self.list_.setHtml(page)


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
    URLsEntitiesRole = Qt.UserRole + 110

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
        message = unicode(index.data(self.MessageRole).toPyObject())
        urls = index.data(self.URLsEntitiesRole).toPyObject()
        for url in urls:
            pretty_url = "<a href='%s'>%s</a>" % (url.url, url.display_text)
            message = message.replace(url.search_for, pretty_url)
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

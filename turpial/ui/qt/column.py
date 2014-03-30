# -*- coding: utf-8 -*-

# Qt widget to implement statuses column in Turpial

#from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import QRect
from PyQt4.QtCore import QLine

from PyQt4.QtGui import QFont
from PyQt4.QtGui import QColor
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QTextDocument
from PyQt4.QtGui import QStyledItemDelegate
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton
from turpial.ui.qt.loader import BarLoadIndicator
from turpial.ui.qt.webview import StatusesWebView

from libturpial.common import get_preview_service_from_url, unescape_list_name, OS_MAC
from libturpial.common.tools import get_account_id_from, get_column_slug_from, get_protocol_from,\
        get_username_from, detect_os

class StatusesColumn(QWidget):
    NOTIFICATION_ERROR = 'error'
    NOTIFICATION_SUCCESS = 'success'
    NOTIFICATION_WARNING = 'warning'
    NOTIFICATION_INFO = 'notice'

    def __init__(self, base, column_id, include_header=True):
        QWidget.__init__(self)
        self.base = base
        self.setMinimumWidth(280)
        self.statuses = []
        self.conversations = {}
        self.id_ = None
        #self.fgcolor = "#e3e3e3"
        #self.fgcolor = "#f9a231"
        #self.updating = False
        self.last_id = None

        self.loader = BarLoadIndicator()
        self.loader.setVisible(False)

        self.webview = StatusesWebView(self.base, self.id_)
        self.webview.link_clicked.connect(self.__link_clicked)
        self.webview.hashtag_clicked.connect(self.__hashtag_clicked)
        self.webview.profile_clicked.connect(self.__profile_clicked)
        self.webview.cmd_clicked.connect(self.__cmd_clicked)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        if include_header:
            header = self.__build_header(column_id)
            layout.addWidget(header)
            layout.addWidget(self.loader)
        layout.addWidget(self.webview, 1)

        self.setLayout(layout)

    def __build_header(self, column_id):
        self.set_column_id(column_id)
        username = get_username_from(self.account_id)
        column_slug = get_column_slug_from(column_id)
        column_slug = unescape_list_name(column_slug)
        column_slug = column_slug.replace('%23', '#')
        column_slug = column_slug.replace('%40', '@')

        #font = QFont('Titillium Web', 18, QFont.Normal, False)
        # This is to handle the 96dpi vs 72dpi screen resolutions on Mac vs the world
        if detect_os() == OS_MAC:
            font = QFont('Maven Pro Light', 25, 0, False)
            font2 = QFont('Monda', 14, 0, False)
        else:
            font = QFont('Maven Pro Light', 16, QFont.Light, False)
            font2 = QFont('Monda', 10, QFont.Light, False)

        bg_style = "background-color: %s; color: %s;" % (self.base.bgcolor, self.base.fgcolor)
        caption = QLabel(username)
        caption.setStyleSheet("QLabel { %s }" % bg_style)
        caption.setFont(font)

        caption2 = QLabel(column_slug)
        caption2.setStyleSheet("QLabel { %s }" % bg_style)
        caption2.setFont(font2)
        caption2.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        caption_box = QHBoxLayout()
        caption_box.setSpacing(8)
        caption_box.addWidget(caption)
        caption_box.addWidget(caption2)
        caption_box.addStretch(1)

        close_button = ImageButton(self.base, 'action-delete-shadowed.png', i18n.get('delete_column'))
        close_button.clicked.connect(self.__delete_column)
        close_button.setStyleSheet("QToolButton { %s border: 0px solid %s;}" % (bg_style, self.base.bgcolor))

        header_layout = QHBoxLayout()
        header_layout.addLayout(caption_box, 1)
        header_layout.addWidget(close_button)

        header = QWidget()
        header.setStyleSheet("QWidget { %s }" % bg_style)
        header.setLayout(header_layout)
        return header

    def __delete_column(self):
        self.base.core.delete_column(self.id_)

    def __link_clicked(self, url):
        url = str(url)
        preview_service = get_preview_service_from_url(url)
        self.base.open_url(url)

    def __hashtag_clicked(self, hashtag):
        self.base.add_search_column(self.account_id, str(hashtag))

    def __profile_clicked(self, username):
        self.base.show_profile_dialog(self.account_id, str(username))

    def __cmd_clicked(self, url):
        status_id = str(url.split(':')[1])
        cmd = url.split(':')[0]
        status = None
        try:
            print 'Seeking for status in self array'
            for status_ in self.statuses:
                if status_.id_ == status_id:
                    status = status_
                    break
            if status is None:
                raise KeyError
        except KeyError:
            print 'Seeking for status in conversations array'
            for status_root, statuses in self.conversations.iteritems():
                for item in statuses:
                    if item.id_ == status_id:
                        status = item
                        break
                if status is not None:
                    break

        if status is None:
            self.notify_error(status_id, i18n.get('try_again'))

        if cmd == 'reply':
            self.__reply_status(status)
        elif cmd == 'quote':
            self.__quote_status(status)
        elif cmd == 'repeat':
            self.__repeat_status(status)
        elif cmd == 'delete':
            self.__delete_status(status)
        elif cmd == 'favorite':
            self.__mark_status_as_favorite(status)
        elif cmd == 'unfavorite':
            self.__unmark_status_as_favorite(status)
        elif cmd == 'delete_direct':
            self.__delete_direct_message(status)
        elif cmd == 'reply_direct':
            self.__reply_direct_message(status)
        elif cmd == 'view_conversation':
            self.__view_conversation(status)
        elif cmd == 'hide_conversation':
            self.__hide_conversation(status)
        elif cmd == 'show_avatar':
            self.__show_avatar(status)

    def __reply_status(self, status):
        self.base.show_update_box_for_reply(self.account_id, status)

    def __quote_status(self, status):
        self.base.show_update_box_for_quote(self.account_id, status)

    def __repeat_status(self, status):
        confirmation = self.base.show_confirmation_message(i18n.get('confirm_retweet'),
            i18n.get('do_you_want_to_retweet_status'))
        if confirmation:
            self.lock_status(status.id_)
            self.base.repeat_status(self.id_, self.account_id, status)

    def __delete_status(self, status):
        confirmation = self.base.show_confirmation_message(i18n.get('confirm_delete'),
            i18n.get('do_you_want_to_delete_status'))
        if confirmation:
            self.lock_status(status.id_)
            self.base.delete_status(self.id_, self.account_id, status)

    def __delete_direct_message(self, status):
        confirmation = self.base.show_confirmation_message(i18n.get('confirm_delete'),
            i18n.get('do_you_want_to_delete_direct_message'))
        if confirmation:
            self.lock_status(status.id_)
            self.base.delete_direct_message(self.id_, self.account_id, status)

    def __reply_direct_message(self, status):
        self.base.show_update_box_for_reply_direct(self.account_id, status)

    def __mark_status_as_favorite(self, status):
        self.lock_status(status.id_)
        self.base.mark_status_as_favorite(self.id_, self.account_id, status)

    def __unmark_status_as_favorite(self, status):
        self.lock_status(status.id_)
        self.base.unmark_status_as_favorite(self.id_, self.account_id, status)

    def __view_conversation(self, status):
        self.webview.view_conversation(status.id_)
        self.base.get_conversation(self.account_id, status, self.id_, status.id_)

    def __hide_conversation(self, status):
        del self.conversations[status.id_]
        self.webview.clear_conversation(status.id_)

    def __show_avatar(self, status):
        self.base.show_profile_image(self.account_id, status.username)

    def __set_last_status_id(self, statuses):
        if statuses[0].repeated_by:
            self.last_id = statuses[0].original_status_id
        else:
            self.last_id = statuses[0].id_

    def set_column_id(self, column_id):
        self.id_ = column_id
        self.account_id = get_account_id_from(column_id)
        self.protocol_id = get_protocol_from(self.account_id)
        self.webview.column_id = column_id

    def clear(self):
        self.webview.clear()

    def start_updating(self):
        self.loader.setVisible(True)
        return self.last_id

    def stop_updating(self):
        self.loader.setVisible(False)

    def update_timestamps(self):
        self.webview.sync_timestamps(self.statuses)

    def update_statuses(self, statuses):
        self.__set_last_status_id(statuses)

        self.update_timestamps()
        self.webview.update_statuses(statuses)

        # Filter repeated statuses
        unique_statuses = [s1 for s1 in statuses if s1 not in self.statuses]

        # Remove old conversations
        to_remove = self.statuses[-(len(unique_statuses)):]
        self.statuses = statuses + self.statuses[: -(len(unique_statuses))]
        for status in to_remove:
            if self.conversations.has_key(status.id_):
                del self.conversations[status.id_]

    def update_conversation(self, status, status_root_id):
        status_root_id = str(status_root_id)
        self.webview.update_conversation(status, status_root_id)
        if status_root_id in self.conversations:
            self.conversations[status_root_id].append(status)
        else:
            self.conversations[status_root_id] = [status]

    def error_in_conversation(self, status_root_id):
        self.webview.clear_conversation(status_root_id)

    def mark_status_as_favorite(self, status_id):
        mark = "setFavorite('%s')" % status_id
        self.webview.execute_javascript(mark)

    def unmark_status_as_favorite(self, status_id):
        mark = "unsetFavorite('%s');" % status_id
        self.webview.execute_javascript(mark)

    def mark_status_as_repeated(self, status_id):
        mark = "setRepeated('%s');" % status_id
        self.webview.execute_javascript(mark)

    def remove_status(self, status_id):
        operation = "removeStatus('%s');" % status_id
        self.webview.execute_javascript(operation)

    def lock_status(self, status_id):
        operation = "lockStatus('%s');" % status_id
        self.webview.execute_javascript(operation)

    def release_status(self, status_id):
        operation = "releaseStatus('%s');" % status_id
        self.webview.execute_javascript(operation)

    def notify(self, id_, type_, message):
        message = message.replace("'", "\"")
        notification = "addNotify('%s', '%s', '%s');" % (id_, type_, message)
        self.webview.execute_javascript(notification)

    def notify_error(self, id_, message):
        self.notify(id_, self.NOTIFICATION_ERROR, message)

    def notify_success(self, id_, message):
        self.notify(id_, self.NOTIFICATION_SUCCESS, message)

    def notify_warning(self, id_, message):
        self.notify(id_, self.NOTIFICATION_WARNING, message)

    def notify_info(self, id_, message):
        self.notify(id_, self.NOTIFICATION_INFO, message)


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

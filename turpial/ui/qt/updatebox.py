# -*- coding: utf-8 -*-

# Qt update box for Turpial

from PyQt4.QtGui import QFont
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QCompleter
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTextCursor
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QFileDialog

from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n
from turpial.ui.qt.loader import BarLoadIndicator
from turpial.ui.qt.widgets import ImageButton, ToggleButton

from libturpial.common.tools import get_urls
from libturpial.common import get_username_from, get_protocol_from

MAX_CHAR = 140

class UpdateBox(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        #self.setParent(base)
        self.base = base
        self.showed = False
        self.setFixedSize(500, 120)
        #self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)

        self.text_edit = CompletionTextEdit()

        self.upload_button = ImageButton(base, 'action-upload.png',
                i18n.get('upload_image'))
        self.short_button = ImageButton(base, 'action-shorten.png',
                i18n.get('short_urls'))

        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.char_count = QLabel('140')
        self.char_count.setFont(font)

        self.update_button = QPushButton(i18n.get('update'))
        self.update_button.setToolTip(self.base.get_shortcut_string('Enter'))
        self.queue_button = QPushButton(i18n.get('add_to_queue'))
        self.queue_button.setToolTip(self.base.get_shortcut_string('P'))

        self.accounts_combo = QComboBox()

        buttons = QHBoxLayout()
        buttons.setSpacing(4)
        buttons.addWidget(self.accounts_combo)
        buttons.addWidget(self.upload_button)
        buttons.addWidget(self.short_button)
        buttons.addStretch(0)
        buttons.addWidget(self.char_count)
        buttons.addWidget(self.queue_button)
        buttons.addWidget(self.update_button)

        self.loader = BarLoadIndicator()
        self.loader.setVisible(False)

        self.error_message = QLabel()

        self.update_button.clicked.connect(self.__update_status)
        self.queue_button.clicked.connect(self.__queue_status)
        self.short_button.clicked.connect(self.__short_urls)
        self.upload_button.clicked.connect(self.__upload_image)
        self.text_edit.textChanged.connect(self.__update_count)
        self.text_edit.quit.connect(self.closeEvent)
        self.text_edit.activated.connect(self.__update_status)
        self.text_edit.enqueued.connect(self.__queue_status)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit, 1)
        layout.addWidget(self.loader)
        layout.addLayout(buttons)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

        self.__clear()

    def __count_chars(self):
        message = self.text_edit.toPlainText()
        urls = [str(url) for url in get_urls(message) if len(url) > 23]
        for url in urls:
            message = message.replace(url, '0' * 23)
        return MAX_CHAR - len(message)

    def __update_count(self):
        remaining_chars = self.__count_chars()
        if remaining_chars <= 10:
            self.char_count.setStyleSheet("QLabel { color: #D40D12 }")
        elif remaining_chars > 10 and remaining_chars <= 20:
            self.char_count.setStyleSheet("QLabel { color: #D4790D }")
        else:
            self.char_count.setStyleSheet("QLabel { color: #000000 }")
        self.char_count.setText(str(remaining_chars))

    def __short_urls(self):
        self.enable(False)
        message = unicode(self.text_edit.toPlainText())
        self.base.short_urls(message)

    def __upload_image(self):
        index = self.accounts_combo.currentIndex()
        account_id = str(self.accounts_combo.itemData(index).toPyObject())
        filename = str(QFileDialog.getOpenFileName(self, i18n.get('upload_image'),
            self.base.home_path))
        if filename != '':
            self.enable(False)
            self.base.upload_media(account_id, filename)

    def __update_status(self):
        index = self.accounts_combo.currentIndex()
        accounts = self.base.core.get_registered_accounts()
        account_id = str(self.accounts_combo.itemData(index).toPyObject())
        message = unicode(self.text_edit.toPlainText())

        if len(message) == 0:
            self.base.show_error_message(i18n.get('empty_message'),
                i18n.get('you_can_not_submit_an_empty_message'))
            return

        if index == 0 and len(accounts) > 1:
            self.base.show_error_message(i18n.get('select_account'),
                i18n.get('select_one_account_to_post'))
            return

        #if len(message) > MAX_CHAR:
        #    self.message.set_error_text(i18n.get('message_looks_like_testament'))
        #    return
        self.enable(False)

        if self.direct_message_to:
            self.base.send_direct_message(account_id, self.direct_message_to, message)
        else:
            if account_id == 'broadcast':
                self.base.broadcast_status(message)
            else:
                self.base.update_status(account_id, message, self.in_reply_to_id)

    def __queue_status(self):
        index = self.accounts_combo.currentIndex()
        accounts = self.base.core.get_registered_accounts()
        account_id = str(self.accounts_combo.itemData(index).toPyObject())
        message = unicode(self.text_edit.toPlainText())

        if len(message) == 0:
            self.base.show_error_message(i18n.get('empty_message'),
                i18n.get('you_can_not_submit_an_empty_message'))
            return

        if index == 0 and len(accounts) > 1:
            self.base.show_error_message(i18n.get('select_account'),
                i18n.get('select_one_account_to_post'))
            return

        self.enable(False)
        self.base.push_status_to_queue(account_id, message)

    def __clear(self):
        self.account_id = None
        self.in_reply_to_id = None
        self.in_reply_to_user = None
        self.direct_message_to = None
        self.message = None
        self.cursor_position = None
        self.text_edit.setText('')
        self.accounts_combo.setCurrentIndex(0)
        self.queue_button.setEnabled(True)
        self.enable(True)
        self.showed = False

    def __show(self):
        self.update_friends_list()
        short_service = self.base.get_shorten_url_service()
        short_tooltip = "%s (%s)" % (i18n.get('short_url'), short_service)
        self.short_button.setToolTip(short_tooltip)
        upload_service = self.base.get_upload_media_service()
        upload_tooltip = "%s (%s)" % (i18n.get('upload_image'), upload_service)
        self.upload_button.setToolTip(upload_tooltip)
        self.accounts_combo.clear()
        accounts = self.base.core.get_registered_accounts()
        if len(accounts) > 1:
            self.accounts_combo.addItem('--', '')
        for account in accounts:
            protocol = get_protocol_from(account.id_)
            icon = QIcon(self.base.get_image_path('%s.png' % protocol))
            self.accounts_combo.addItem(icon, get_username_from(account.id_), account.id_)
        if len(accounts) > 1:
            icon = QIcon(self.base.get_image_path('action-conversation.png'))
            self.accounts_combo.addItem(icon, i18n.get('broadcast'), 'broadcast')
        if self.account_id:
            index = self.accounts_combo.findData(self.account_id)
            if index > 0:
                self.accounts_combo.setCurrentIndex(index)
            self.accounts_combo.setEnabled(False)
        if self.message:
            self.text_edit.setText(self.message)
            cursor = self.text_edit.textCursor()
            cursor.movePosition(self.cursor_position, QTextCursor.MoveAnchor)
            self.text_edit.setTextCursor(cursor)

        QWidget.show(self)
        self.showed = True

    def show(self):
        if self.showed:
            return self.raise_()
        self.setWindowTitle(i18n.get('whats_happening'))
        self.__show()

    def show_for_reply(self, account_id, status):
        if self.showed:
            return self.raise_()
        title = "%s @%s" % (i18n.get('reply_to'), status.username)
        self.setWindowTitle(title)
        self.account_id = account_id
        self.in_reply_to_id = status.id_
        self.in_reply_to_user = status.username
        mentions = ' '.join(["@%s" % user for user in status.get_mentions()])
        self.message = "%s " % mentions
        self.cursor_position = QTextCursor.End
        self.__show()
        self.queue_button.setEnabled(False)

    def show_for_send_direct(self, account_id, username):
        if self.showed:
            return self.raise_()
        title = "%s @%s" % (i18n.get('send_message_to'), username)
        self.setWindowTitle(title)
        self.account_id = account_id
        self.direct_message_to = username
        self.__show()
        self.queue_button.setEnabled(False)

    def show_for_reply_direct(self, account_id, status):
        if self.showed:
            return self.raise_()
        title = "%s @%s" % (i18n.get('send_message_to'), status.username)
        self.setWindowTitle(title)
        self.account_id = account_id
        self.direct_message_to = status.username
        self.__show()
        self.queue_button.setEnabled(False)

    def show_for_quote(self, account_id, status):
        if self.showed:
            return self.raise_()
        self.setWindowTitle(i18n.get('quoting'))
        self.account_id = account_id
        self.message = " RT @%s %s" % (status.username, status.text)
        self.cursor_position = QTextCursor.Start
        self.__show()
        self.queue_button.setEnabled(False)

    def closeEvent(self, event=None):
        message = unicode(self.text_edit.toPlainText())

        if len(message) > 0:
            confirmation = self.base.show_confirmation_message(i18n.get('confirm_discard'),
                i18n.get('do_you_want_to_discard_message'))
            if not confirmation:
                return

        if event:
            event.ignore()
        self.__clear()
        self.hide()

    def enable(self, value):
        self.text_edit.setEnabled(value)
        if not self.account_id:
            self.accounts_combo.setEnabled(value)
        self.upload_button.setEnabled(value)
        self.short_button.setEnabled(value)
        self.update_button.setEnabled(value)
        self.queue_button.setEnabled(value)
        self.loader.setVisible(not value)

    def done(self):
        self.__clear()
        self.hide()

    def after_short_url(self, message):
        self.text_edit.setText(message)
        self.enable(True)

    def after_upload_media(self, media_url):
        text_cursor = self.text_edit.textCursor()
        text_cursor.select(QTextCursor.WordUnderCursor)
        if text_cursor.selectedText() != '':
            media_url = " %s" % media_url
        text_cursor.clearSelection()
        text_cursor.insertText(media_url)
        self.text_edit.setTextCursor(text_cursor)
        self.enable(True)

    def update_friends_list(self):
        completer = QCompleter(self.base.load_friends_list_with_extras())
        self.text_edit.setCompleter(completer)


class CompletionTextEdit(QTextEdit):
    IGNORED_KEYS = (
        Qt.Key_Enter,
        Qt.Key_Return,
        Qt.Key_Escape,
        Qt.Key_Tab,
        Qt.Key_Backtab
    )

    quit = pyqtSignal()
    activated = pyqtSignal()
    enqueued = pyqtSignal()

    def __init__(self):
        QTextEdit.__init__(self)
        self.completer = None
        self.setAcceptRichText(False)

    def setCompleter(self, completer):
        if self.completer:
            self.completer.activated.disconnect()

        self.completer = completer
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        if self.completer.widget() != self:
            return

        tc = self.textCursor()
        extra = (completion.length() - self.completer.completionPrefix().length())
        tc.movePosition(QTextCursor.StartOfWord)
        tc.select(QTextCursor.WordUnderCursor)
        tc.insertText(''.join([str(completion), ' ']))
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        text = ""
        while True:
            tc.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            text = tc.selectedText()
            if tc.position() == 0:
                break
            if text.startsWith(' '):
                text = text[1:]
                break

        return text

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        #print self.completer
        if self.completer and self.completer.popup().isVisible():
            if event.key() in self.IGNORED_KEYS:
                event.ignore()
                print 'ignoring'
                return

        if event.key() == Qt.Key_Escape:
            self.quit.emit()
            return

        QTextEdit.keyPressEvent(self, event)

        hasModifier = event.modifiers() != Qt.NoModifier
        enterKey = event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return
        queueKey = event.key() == Qt.Key_P

        if hasModifier and event.modifiers() == Qt.ControlModifier and enterKey:
            self.activated.emit()
            return

        if hasModifier and event.modifiers() == Qt.ControlModifier and queueKey:
            self.enqueued.emit()
            return

        completionPrefix = self.textUnderCursor()

        if hasModifier or event.text().isEmpty() or not completionPrefix.startsWith('@'):
            self.completer.popup().hide()
            #print 'me fui', event.key(), int(event.modifiers())
            return

        if completionPrefix.startsWith('@') and completionPrefix[1:] != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completionPrefix[1:])
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))

        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0)
                + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursor_rect)



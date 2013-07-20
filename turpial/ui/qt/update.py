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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import SIGNAL

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton, ToggleButton

from libturpial.common import get_username_from, get_protocol_from


class UpdateBox(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('whats_happening'))
        self.setFixedSize(500, 120)
        #self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)

        completer = QCompleter(['one', 'two', 'carlos', 'maria',
            'ana', 'carolina', 'alberto', 'pedro', 'tomas'])

        self.text = CompletionTextEdit()
        self.text.setCompleter(completer)

        upload_button = ImageButton(base, 'action-upload.png',
                i18n.get('upload_image'))
        short_button = ImageButton(base, 'action-shorten.png',
                i18n.get('short_urls'))

        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.char_count = QLabel('140')
        self.char_count.setFont(font)

        update_button = QPushButton(i18n.get('update'))

        icon = QIcon(base.get_image_path('twitter.png'))
        accounts = QComboBox()
        accounts.addItem(icon, 'satanas82')
        accounts.addItem(icon, 'turpialve')
        icon = QIcon(base.get_image_path('action-conversation.png'))
        accounts.addItem(icon, 'Broadcast')

        buttons = QHBoxLayout()
        buttons.addWidget(accounts)
        buttons.addWidget(upload_button)
        buttons.addWidget(short_button)
        buttons.addStretch(0)
        buttons.addWidget(self.char_count)
        buttons.addWidget(update_button)

        layout = QVBoxLayout()
        layout.addWidget(self.text, 1)
        layout.addLayout(buttons)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

class CompletionTextEdit(QTextEdit):
    IGNORED_KEYS = (
        Qt.Key_Enter,
        Qt.Key_Return,
        Qt.Key_Escape,
        Qt.Key_Tab,
        Qt.Key_Backtab
    )

    def __init__(self):
        QTextEdit.__init__(self)
        self.completer = None

    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)

        self.completer = completer
        self.completer.setWidget(self)
        self.completer.activated.connect(self.insertCompletion)

    def insertCompletion(self, completion):
        if self.completer.widget() != self:
            return

        tc = self.textCursor()
        extra = (completion.length() - self.completer.completionPrefix().length())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion.right(extra))
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
        if self.completer and self.completer.popup().isVisible():
            if event.key() in self.IGNORED_KEYS:
                event.ignore()
                return

        QTextEdit.keyPressEvent(self, event)

        hasModifier = event.modifiers() != Qt.NoModifier

        completionPrefix = self.textUnderCursor()

        if hasModifier or event.text().isEmpty() or not completionPrefix.startsWith('@'):
            self.completer.popup().hide()
            return

        if completionPrefix.startsWith('@') and completionPrefix[1:] != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completionPrefix[1:])
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))

        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0) 
                + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursor_rect)



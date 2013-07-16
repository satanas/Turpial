# -*- coding: utf-8 -*-

# Qt update box for Turpial

from PyQt4.QtGui import QFont
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QTextEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

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

        self.text = QTextEdit()

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

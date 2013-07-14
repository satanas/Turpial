# -*- coding: utf-8 -*-

# Qt OAuth dialog for Turpial

from PyQt4.QtGui import QFont
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QGridLayout

from PyQt4.QtCore import Qt

from turpial.ui.lang import i18n
from turpial.ui.qt.widgets import ImageButton, VLine, HLine


class ProfileDialog(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('user_profile'))
        self.setFixedSize(350, 320)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)

        username = QLabel('<b>@satanas82</b>')
        username.setTextFormat(Qt.RichText)

        fullname = QLabel('Full name bla bla')
        options = ImageButton(base, 'action-status-menu.png',
                i18n.get(''))

        verified_icon = QLabel()
        verified_icon.setPixmap(base.load_image('mark-verified.png', True))

        protected_icon = QLabel()
        protected_icon.setPixmap(base.load_image('mark-protected.png', True))

        avatar = QLabel()
        avatar.setPixmap(base.load_image('unknown.png', True))

        info_line1 = QHBoxLayout()
        info_line1.setSpacing(5)
        info_line1.addWidget(username)
        info_line1.addSpacing(5)
        info_line1.addWidget(verified_icon)
        info_line1.addWidget(protected_icon)
        info_line1.addStretch(0)

        info_line2 = QHBoxLayout()
        info_line2.addWidget(fullname, 1)
        info_line2.addWidget(options)

        user_info = QVBoxLayout()
        user_info.addLayout(info_line1)
        user_info.addLayout(info_line2)

        header = QHBoxLayout()
        header.setContentsMargins(10, 10 ,10, 0)
        header.addWidget(avatar)
        header.addSpacing(10)
        header.addLayout(user_info)

        bio = UserInfoBox(base, 'bio', 'icon-bio.png')
        bio.set_word_wrap(True)
        bio.set_text('bla bla bla bla blansjkda alkslkja akljdklasjdasd')

        location = UserInfoBox(base, 'location', 'icon-location.png')
        location.set_text('Lorem Ipsum')

        web = UserInfoBox(base, 'web', 'icon-home.png')
        web.set_text('http://bla.com')

        body = QVBoxLayout()
        body.setSpacing(15)
        body.setContentsMargins(10, 0, 10, 10)
        body.addLayout(bio)
        body.addLayout(location)
        body.addLayout(web)

        tweets = StatInfoBox('tweets', '999')
        following = StatInfoBox('following', '9999999')
        followers = StatInfoBox('followers', '9999999')
        favorites = StatInfoBox('favorites', '9999')

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 5, 0, 10)
        footer.setSpacing(1)
        footer.addLayout(tweets)
        footer.addWidget(VLine())
        footer.addLayout(following)
        footer.addWidget(VLine())
        footer.addLayout(followers)
        footer.addWidget(VLine())
        footer.addLayout(favorites)

        footer_widget = QWidget()
        footer_widget.setLayout(footer)
        footer_widget.setStyleSheet("QWidget { background-color: #333; color: white; }")

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(HLine())
        layout.addLayout(body, 1)
        layout.addWidget(footer_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

class UserInfoBox(QVBoxLayout):
    def __init__(self, base, title, image, text=None, text_as_link=False):
        QVBoxLayout.__init__(self)
        icon = QLabel()
        icon.setPixmap(base.load_image(image, True))
        caption = QLabel("<b>%s</b>" % i18n.get(title))
        header = QHBoxLayout()
        header.addWidget(icon)
        header.addWidget(caption, 1)

        if text:
            self.text = QLabel(text)
        else:
            self.text = QLabel()

        self.setSpacing(5)
        self.addLayout(header)
        self.addWidget(self.text)

    def set_text(self, text):
        self.text.setText(text)

    def set_word_wrap(self, value):
        self.text.setWordWrap(value)

class StatInfoBox(QVBoxLayout):
    def __init__(self, title, value=None):
        QVBoxLayout.__init__(self)
        value = value or '0'

        font = QFont()
        font.setPointSize(18)
        font.setBold(True)

        self.stat = QLabel("<b>%s</b>" % value)
        self.stat.setAlignment(Qt.AlignCenter)
        self.stat.setFont(font)

        font2 = QFont()
        font2.setPointSize(10)
        caption = QLabel(i18n.get(title))
        caption.setAlignment(Qt.AlignCenter)
        caption.setFont(font2)

        self.setSpacing(5)
        self.setContentsMargins(0, 0, 0, 0)
        self.addWidget(self.stat)
        self.addWidget(caption)


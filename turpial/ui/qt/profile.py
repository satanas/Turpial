# -*- coding: utf-8 -*-

# Qt OAuth dialog for Turpial

from PyQt4.QtGui import QFont
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QGridLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n
from turpial.ui.qt.loader import BarLoadIndicator
from turpial.ui.qt.widgets import ImageButton, VLine, HLine

from libturpial.common.tools import get_username_from


class ProfileDialog(QWidget):

    options_clicked = pyqtSignal(QPoint, object)

    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.account_id = None
        self.setWindowTitle(i18n.get('user_profile'))
        self.setFixedSize(350, 350)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.CustomizeWindowHint)
        self.setStyleSheet("QWidget { background-color: #fff; }")

        self.username = QLabel('')
        self.username.setTextFormat(Qt.RichText)

        self.fullname = QLabel('')
        self.options = ImageButton(base, 'action-status-menu.png',
                i18n.get(''))
        self.options.clicked.connect(self.__options_clicked)

        self.verified_icon = QLabel()
        self.verified_icon.setPixmap(base.load_image('mark-verified.png', True))

        self.protected_icon = QLabel()
        self.protected_icon.setPixmap(base.load_image('mark-protected.png', True))

        self.avatar = QLabel()
        self.avatar.setPixmap(base.load_image('unknown.png', True))

        self.you_label = QLabel(i18n.get('this_is_you'))
        self.you_label.setVisible(False)

        info_line1 = QHBoxLayout()
        info_line1.setSpacing(5)
        info_line1.addWidget(self.username)
        info_line1.addSpacing(5)
        info_line1.addWidget(self.verified_icon)
        info_line1.addWidget(self.protected_icon)
        info_line1.addStretch(0)

        info_line2 = QHBoxLayout()
        info_line2.addWidget(self.fullname, 1)
        info_line2.addWidget(self.options)
        info_line2.addWidget(self.you_label)

        user_info = QVBoxLayout()
        user_info.addLayout(info_line1)
        user_info.addLayout(info_line2)

        self.loader = BarLoadIndicator()
        self.loader.setVisible(False)

        header = QHBoxLayout()
        header.setContentsMargins(10, 10 ,10, 0)
        header.addWidget(self.avatar)
        header.addSpacing(10)
        header.addLayout(user_info)


        self.bio = UserInfoBox(base, 'bio', 'icon-bio.png')
        self.bio.set_word_wrap(True)
        self.bio.set_info('')

        self.location = UserInfoBox(base, 'location', 'icon-location.png')
        self.location.set_info('')

        self.web = UserInfoBox(base, 'web', 'icon-home.png')
        self.web.set_info('')

        body = QVBoxLayout()
        body.setSpacing(15)
        body.setContentsMargins(10, 0, 10, 10)
        body.addLayout(self.bio)
        body.addLayout(self.location)
        body.addLayout(self.web)

        self.tweets = StatInfoBox('tweets', '')
        self.following = StatInfoBox('following', '')
        self.followers = StatInfoBox('followers', '')
        self.favorites = StatInfoBox('favorites', '')

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 5, 0, 10)
        footer.setSpacing(1)
        footer.addLayout(self.tweets)
        footer.addWidget(VLine())
        footer.addLayout(self.following)
        footer.addWidget(VLine())
        footer.addLayout(self.followers)
        footer.addWidget(VLine())
        footer.addLayout(self.favorites)

        footer_widget = QWidget()
        footer_widget.setLayout(footer)
        footer_widget.setStyleSheet("QWidget { background-color: #333; color: white; }")

        self.hline = HLine()
        self.hline.setMinimumHeight(2)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addSpacing(10)
        layout.addWidget(self.hline)
        layout.addWidget(self.loader)
        layout.addSpacing(10)
        layout.addLayout(body, 1)
        layout.addWidget(footer_widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.__clear()

    def __clear(self):
        self.profile = None
        self.account_id = None
        self.verified_icon.setVisible(False)
        self.protected_icon.setVisible(False)
        self.you_label.setVisible(False)
        self.options.setVisible(False)
        self.avatar.setPixmap(self.base.load_image('unknown.png', True))
        self.bio.set_info('')
        self.location.set_info('')
        self.web.set_info('')
        self.tweets.set_value('')
        self.following.set_value('')
        self.followers.set_value('')
        self.favorites.set_value('')

    def __options_clicked(self):
        self.options_clicked.emit(QCursor.pos(), self.profile)

    def start_loading(self, profile_username):
        self.__clear()
        self.hline.setVisible(False)
        self.loader.setVisible(True)
        self.username.setText('<b>%s</b>' % profile_username)
        self.fullname.setText(i18n.get('loading'))
        self.show()

    def loading_finished(self, profile, account_id):
        self.profile = profile
        self.account_id = account_id
        self.loader.setVisible(False)
        self.hline.setVisible(False)
        self.username.setText('<b>%s</b>' % profile.username)
        self.fullname.setText(profile.fullname)

        if get_username_from(account_id) == profile.username:
            self.you_label.setVisible(True)
            self.options.setVisible(False)
        else:
            self.you_label.setVisible(False)
            self.options.setVisible(True)
        self.verified_icon.setVisible(profile.verified)
        self.protected_icon.setVisible(profile.protected)
        self.avatar.setPixmap(self.base.load_image('unknown.png', True))
        self.bio.set_info(profile.bio)
        self.location.set_info(profile.location)
        self.web.set_info(profile.url)
        self.tweets.set_value(str(profile.statuses_count))
        self.following.set_value(str(profile.friends_count))
        self.followers.set_value(str(profile.followers_count))
        self.favorites.set_value(str(profile.favorites_count))
        self.show()



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

    def set_info(self, text=None):
        if text is not None:
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

        self.stat = QLabel(value)
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

    def set_value(self, value):
        self.stat.setText(value)


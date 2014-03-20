# -*- coding: utf-8 -*-

# Qt profile dialog for Turpial

from PyQt4.QtGui import QFont
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QPoint
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n
from turpial.ui.qt.column import StatusesColumn
from turpial.ui.qt.webview import ProfileHeaderWebview
from turpial.ui.qt.widgets import ImageButton, VLine, HLine, Window, ErrorLabel, BarLoadIndicator

from libturpial.common.tools import get_username_from


class ProfileDialog(Window):

    options_clicked = pyqtSignal(QPoint, object)

    def __init__(self, base):
        Window.__init__(self, base, i18n.get('user_profile'))
        self.account_id = None
        self.setFixedSize(380, 500)

        self.this_is_you_label = QPushButton(i18n.get('this_is_you'))
        self.this_is_you_label.setEnabled(False)
        #self.this_is_you.setVisible(False)

        self.loader = BarLoadIndicator()
        #self.loader.setVisible(False)

        self.header = ProfileHeader(base)

        self.options_button = ImageButton(base, 'action-status-menu.png', i18n.get(''))
        self.options_button.clicked.connect(self.__options_clicked)

        self.follows_you_label = QPushButton(i18n.get('follows_you'))
        self.follows_you_label.setEnabled(False)
        #self.follows_you_label.setVisible(False)

        self.error_message = ErrorLabel()
        #self.error_message.setVisible(False)

        self.follow_button = QPushButton()

        self.loading_label = QLabel(i18n.get('loading'))

        options_box = QHBoxLayout()
        options_box.setContentsMargins(5, 5, 5, 5)
        options_box.setSpacing(5)
        options_box.addWidget(self.options_button)
        options_box.addStretch(1)
        options_box.addWidget(self.error_message)
        options_box.addWidget(self.follows_you_label)
        options_box.addWidget(self.follow_button)
        options_box.addWidget(self.this_is_you_label)
        options_box.addWidget(self.loading_label)

        self.last_statuses = StatusesColumn(self.base, None, False)

        self.tweets = StatInfoBox('tweets', '')
        self.following = StatInfoBox('following', '')
        self.followers = StatInfoBox('followers', '')

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 5, 0, 10)
        footer_layout.setSpacing(0)
        footer_layout.addLayout(self.tweets)
        footer_layout.addWidget(VLine())
        footer_layout.addLayout(self.following)
        footer_layout.addWidget(VLine())
        footer_layout.addLayout(self.followers)

        footer = QWidget()
        footer.setLayout(footer_layout)
        footer.setStyleSheet("QWidget { background-color: #333; color: white; }")

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.loader)
        layout.addWidget(self.header)
        layout.addLayout(options_box)
        layout.addWidget(self.last_statuses)
        layout.addWidget(footer)
        self.setLayout(layout)

        self.__clear()

    def __clear(self):
        self.profile = None
        self.showed = False
        self.account_id = None
        self.loader.setVisible(False)
        self.options_button.setEnabled(False)
        self.error_message.setVisible(False)
        self.follows_you_label.setVisible(False)
        self.follow_button.setVisible(False)
        self.this_is_you_label.setVisible(False)
        self.loading_label.setVisible(False)
        self.tweets.set_value('')
        self.following.set_value('')
        self.followers.set_value('')
        self.header.clear()
        self.last_statuses.id_ = None
        self.last_statuses.clear()

    def __options_clicked(self):
        self.options_clicked.emit(QCursor.pos(), self.profile)

    def __show_avatar(self):
        self.base.show_profile_image(self.account_id, self.profile.username)

    def __on_timeout(self):
        self.error_message.setText('')
        self.error_message.setVisible(False)

    def closeEvent(self, event=None):
        if event:
            event.ignore()
        self.__clear()
        self.hide()

    def start_loading(self, profile_username):
        self.__clear()
        self.loader.setVisible(True)
        self.loading_label.setVisible(True)
        self.options_button.setEnabled(False)
        self.show()
        self.raise_()
        self.showed = True

    def loading_finished(self, profile, account_id):
        self.profile = profile
        self.account_id = str(account_id)
        self.loader.setVisible(False)
        self.loading_label.setVisible(False)
        it_is_you = get_username_from(account_id) == profile.username

        if it_is_you:
            self.this_is_you_label.setVisible(True)
            self.follow_button.setVisible(False)
            self.options_button.setEnabled(False)
        else:
            self.this_is_you_label.setVisible(False)
            self.follow_button.setVisible(True)
            self.options_button.setEnabled(True)

        if profile.followed_by and not it_is_you:
            self.follows_you_label.setVisible(True)

        #if profile.following:
        #    self.follow_button.setVisible(True)

        self.tweets.set_value(str(profile.statuses_count))
        self.following.set_value(str(profile.friends_count))
        self.followers.set_value(str(profile.followers_count))

        self.header.update_profile(profile)
        column_id = "%s-profile_recent" % self.account_id
        self.last_statuses.set_column_id(column_id)
        self.last_statuses.update_statuses(profile.recent_updates)
        self.show()
        self.raise_()

    def is_for_profile(self, column_id):
        if column_id.find('profile_recent') > 0:
            return True
        return False

    def update_avatar(self, image_path, username):
        if username != self.profile.username or not self.showed:
            return
        self.avatar.setPixmap(self.base.load_image(image_path, True))

    def update_following(self, username, following):
        if username != self.profile.username or not self.showed:
            return
        self.profile.following = following

    def error(self, message):
        self.loader.setVisible(False)
        self.hline.setVisible(False)
        self.fullname.setText('')
        self.error_message.setText(message)
        self.error_message.setVisible(True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.__on_timeout)
        self.timer.start(5000)
        self.show()
        self.raise_()

    def error_marking_status_as_favorite(self, status_id):
        self.last_statuses.release_status(status_id)
        self.last_statuses.notify_error(status_id, i18n.get('error_marking_status_as_favorite'))

    def error_unmarking_status_as_favorite(self, status_id):
        self.last_statuses.release_status(status_id)
        self.last_statuses.notify_error(status_id, i18n.get('error_unmarking_status_as_favorite'))

    def error_repeating_status(self, status_id):
        self.last_statuses.release_status(status_id)
        self.last_statuses.notify_error(status_id, i18n.get('error_repeating_status'))

    def error_loading_conversation(self, status_root_id):
        self.last_statuses.error_in_conversation(status_root_id)
        self.last_statuses.notify_error(self.base.random_id(), i18n.get('error_loading_conversation'))


class ProfileHeader(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)
        self.setStyleSheet("QWidget { background-color: #fff; }")
        self.webview = ProfileHeaderWebview(base)

    def clear(self):
        self.webview.clear()

    def update_profile(self, profile):
        self.webview.update_profile(profile)


class UserField(QVBoxLayout):
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
        self.text.setOpenExternalLinks(True);

        self.setSpacing(5)
        self.setContentsMargins(10, 0, 10, 0)
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
        font.setPointSize(16)
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

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        QLabel.__init__(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

# -*- coding: utf-8 -*-

# Qt preferences dialog for Turpial

from datetime import datetime, timedelta

from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QSlider
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QButtonGroup
from PyQt4.QtGui import QRadioButton
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n

from turpial.ui.qt.widgets import Window

#TODO: Enable tp open dialog in a specific tab
class PreferencesDialog(Window):
    def __init__(self, base):
        Window.__init__(self, base, i18n.get('preferences'))
        self.setFixedSize(450, 360)
        self.current_config = self.base.get_config()

        self.tabbar = QTabWidget()
        self.tabbar.setTabsClosable(False)
        self.tabbar.setMovable(False)
        self.tabbar.setUsesScrollButtons(True)
        self.tabbar.setElideMode(Qt.ElideNone)

        self.general_page = GeneralPage(base)
        self.notifications_page = NotificationsPage(base)
        self.services_page = ServicesPage(base)
        self.browser_page = BrowserPage(base)
        self.proxy_page = ProxyPage(base)
        self.advanced_page = AdvancedPage(base)

        self.tabbar.addTab(self.general_page, i18n.get('general'))
        self.tabbar.addTab(self.notifications_page, i18n.get('notifications'))
        self.tabbar.addTab(self.services_page, i18n.get('services'))
        self.tabbar.addTab(self.browser_page, i18n.get('web_browser'))
        self.tabbar.addTab(self.proxy_page, i18n.get('proxy'))
        self.tabbar.addTab(self.advanced_page, i18n.get('advanced'))

        self.save_button = QPushButton(i18n.get('save'))
        self.save_button.clicked.connect(self.__on_save)
        self.close_button = QPushButton(i18n.get('close'))
        self.close_button.clicked.connect(self.__on_close)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.setSpacing(4)
        button_box.addWidget(self.close_button)
        button_box.addWidget(self.save_button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tabbar, 1)
        vbox.addLayout(button_box)
        vbox.setContentsMargins(10, 10, 10, 10)
        self.setLayout(vbox)
        self.show()

    def __on_close(self):
        self.close()

    def __on_save(self):
        notif, sounds = self.notifications_page.get_config()

        new_config = {
            'General': self.general_page.get_config(),
            'Notifications': notif,
            'Sounds': sounds,
            'Services': self.services_page.get_config(),
            'Browser': self.browser_page.get_config(),
            'Proxy': self.proxy_page.get_config(),
            'Advanced': self.advanced_page.get_config()
        }
        self.base.update_config(new_config)
        self.close()

class BasePage(QWidget):
    def __init__(self, caption):
        QWidget.__init__(self)

        description = QLabel(caption)
        description.setWordWrap(True)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(description)
        self.layout.addSpacing(15)
        self.layout.setSpacing(5)

        self.setLayout(self.layout)

class GeneralPage(BasePage):
    def __init__(self, base):
        BasePage.__init__(self, i18n.get('general_tab_description'))

        update_frecuency = base.core.get_update_interval()
        queue_frecuency = base.core.get_queue_interval()
        statuses = base.core.get_statuses_per_column()
        minimize_on_close = base.core.get_minimize_on_close()

        self.update_frecuency = Slider(i18n.get('update_frecuency'), unit='min',
            default_value=update_frecuency)
        self.statuses_per_column = Slider(i18n.get('statuses_per_column'), minimum_value=20,
            maximum_value=200, default_value=statuses)
        self.queue_frecuency = Slider(i18n.get('queue_frecuency'), minimum_value=5,
            maximum_value=720, default_value=queue_frecuency, single_step=15, time=True)
        self.minimize_on_close = CheckBox(i18n.get('minimize_on_close'), checked=minimize_on_close)

        self.layout.addWidget(self.update_frecuency)
        self.layout.addWidget(self.queue_frecuency)
        self.layout.addWidget(self.statuses_per_column)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.minimize_on_close)
        self.layout.addStretch(1)

    def get_config(self):
        minimize = 'on' if self.minimize_on_close.get_value() else 'off'

        return {
            'update-interval': self.update_frecuency.get_value(),
            'statuses': self.statuses_per_column.get_value(),
            'queue-interval': self.queue_frecuency.get_value(),
            'minimize-on-close': minimize
        }

class NotificationsPage(BasePage):
    def __init__(self, base):
        BasePage.__init__(self, i18n.get('notifications_tab_description'))

        notify_on_updates = base.core.get_notify_on_updates()
        notify_on_actions = base.core.get_notify_on_actions()
        sound_on_login = base.core.get_sound_on_login()
        sound_on_updates = base.core.get_sound_on_updates()

        self.notify_on_updates = CheckBox(i18n.get('notify_on_updates'), checked=notify_on_updates)
        self.notify_on_actions = CheckBox(i18n.get('notify_on_actions'), checked=notify_on_actions)
        self.sound_on_login = CheckBox(i18n.get('sound_on_login'), checked=sound_on_login)
        self.sound_on_updates = CheckBox(i18n.get('sound_on_updates'), checked=sound_on_updates)

        self.layout.addWidget(self.notify_on_updates)
        self.layout.addWidget(self.notify_on_actions)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.sound_on_login)
        self.layout.addWidget(self.sound_on_updates)
        self.layout.addStretch(1)

    def get_config(self):
        notif = {
            'updates': 'on' if self.notify_on_updates.get_value() else 'off',
            'actions': 'on' if self.notify_on_actions.get_value() else 'off'

        }
        sound = {
            'login': 'on' if self.sound_on_login.get_value() else 'off',
            'updates': 'on' if self.sound_on_updates.get_value() else 'off'
        }
        return notif, sound

class ServicesPage(BasePage):
    def __init__(self, base):
        BasePage.__init__(self, i18n.get('services_tab_description'))

        short_url_services = base.core.get_available_short_url_services()
        default_short_url_service = base.core.get_shorten_url_service()
        self.short_url = ComboBox(i18n.get('short_urls'), short_url_services, default_short_url_service,
            expand_combo=True)

        upload_media_services = base.core.get_available_upload_media_services()
        default_upload_media_service = base.core.get_upload_media_service()
        self.upload_media = ComboBox(i18n.get('upload_image'), upload_media_services,
                default_upload_media_service, expand_combo=True)

        self.layout.addWidget(self.short_url)
        self.layout.addSpacing(5)
        self.layout.addWidget(self.upload_media)
        self.layout.addStretch(1)

    def get_config(self):
        return {
            'shorten-url': self.short_url.get_value(),
            'upload-pic': self.upload_media.get_value()
        }

class BrowserPage(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)

        current_browser = base.core.get_default_browser()

        description = QLabel(i18n.get('web_browser_tab_description'))
        description.setWordWrap(True)

        self.command = QLineEdit()

        self.default_browser = RadioButton(i18n.get('use_default_browser'), self)
        self.default_browser.selected.connect(self.__on_defaul_selected)
        self.custom_browser = RadioButton(i18n.get('set_custom_browser'), self)
        self.custom_browser.selected.connect(self.__on_custom_selected)

        custom_label = QLabel(i18n.get('command'))
        self.open_button = QPushButton(i18n.get('open'))
        command_box = QHBoxLayout()
        command_box.setSpacing(5)
        command_box.addWidget(custom_label)
        command_box.addWidget(self.command, 1)
        command_box.addWidget(self.open_button)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.default_browser.radiobutton)
        self.button_group.addButton(self.custom_browser.radiobutton)
        self.button_group.setExclusive(True)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(5, 5, 5, 0)
        vbox.addWidget(description)
        vbox.addSpacing(15)
        vbox.addWidget(self.default_browser)
        vbox.addSpacing(10)
        vbox.addWidget(self.custom_browser)
        vbox.addLayout(command_box)
        vbox.addStretch(1)

        self.setLayout(vbox)

        if current_browser == '':
            self.default_browser.set_value(True)
            self.command.setText('')
            self.__on_defaul_selected()
        else:
            self.custom_browser.set_value(True)
            self.command.setText(current_browser)
            self.__on_custom_selected()

    def __on_defaul_selected(self):
        self.open_button.setEnabled(False)
        self.command.setEnabled(False)

    def __on_custom_selected(self):
        self.open_button.setEnabled(True)
        self.command.setEnabled(True)

    def get_config(self):
        if self.default_browser.get_value():
            cmd = ''
        else:
            cmd = str(self.command.text())
        return { 'cmd': cmd }

class ProxyPage(BasePage):
    def __init__(self, base):
        BasePage.__init__(self, i18n.get('proxy_tab_description'))

        config = base.core.get_proxy_configuration()
        if config['username'] != '':
            default_authenticated = True
        else:
            default_authenticated = False

        self.protocol = ComboBox(i18n.get('type'), ['HTTP', 'HTTPS'], 'HTTP', expand_combo=True)
        self.host = LineEdit(i18n.get('host'), default_value=config['server'])
        self.port = LineEdit(i18n.get('port'), text_size=100, default_value=config['port'])
        self.authenticated = CheckBox(i18n.get('with_authentication'), checked=default_authenticated)
        self.authenticated.status_changed.connect(self.__on_click_authenticated)
        self.username = LineEdit(i18n.get('username'), default_value=config['username'])
        self.password = LineEdit(i18n.get('password'), default_value=config['password'])

        self.layout.addWidget(self.protocol)
        self.layout.addWidget(self.host)
        self.layout.addWidget(self.port)
        self.layout.addWidget(self.authenticated)
        self.layout.addWidget(self.username)
        self.layout.addWidget(self.password)
        self.layout.addStretch(1)

        self.__on_click_authenticated(default_authenticated)

    def __on_click_authenticated(self, checked):
        self.__show_authentication_widgets(checked)

    def __show_authentication_widgets(self, visible):
        self.username.set_visible(visible)
        self.password.set_visible(visible)

    def get_config(self):
        if self.authenticated.get_value():
            username = self.username.get_value()
            password = self.password.get_value()
        else:
            username = ''
            password = ''

        return {
            'protocol': self.protocol.get_value(),
            'server': self.host.get_value(),
            'port': self.port.get_value(),
            'username': username,
            'password': password
        }

class AdvancedPage(BasePage):
    def __init__(self, base):
        BasePage.__init__(self, i18n.get('advanced_tab_description'))

        socket_timeout = base.core.get_socket_timeout()
        show_avatars = base.core.get_show_user_avatars()

        clean_cache_caption = "%s\n(%s)" % (i18n.get('delete_all_files_in_cache'), base.get_cache_size())
        self.clean_cache = PushButton(clean_cache_caption, i18n.get('clean_cache'))
        self.clean_cache.clicked.connect(self.__on_clean_cache)
        self.restore_config = PushButton(i18n.get('restore_config_to_default'), i18n.get('restore_config'))
        self.restore_config.clicked.connect(self.__on_config_restore)
        self.socket_timeout = Slider(i18n.get('socket_timeout'), default_value=socket_timeout,
            minimum_value=5, maximum_value=120, unit='sec')
        self.show_avatars = CheckBox(i18n.get('show_avatars'), checked=show_avatars)

        self.layout.addWidget(self.clean_cache)
        self.layout.addWidget(self.restore_config)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.socket_timeout)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.show_avatars)
        self.layout.addStretch(1)

    def __on_clean_cache(self):
        self.base.clean_cache()
        clean_cache_caption = "%s\n(0 B)" % (i18n.get('delete_all_files_in_cache'))
        self.clean_cache.button.setEnabled(False)
        self.clean_cache.description.setText(clean_cache_caption)

    def __on_config_restore(self):
        print 'restoring config'

    def get_config(self):
        show_avatars = 'on' if self.show_avatars.get_value() else 'off'
        return {
            'socket-timeout': self.socket_timeout.get_value(),
            'show-user-avatars': show_avatars
        }


################################################################################
### Widgets
################################################################################

# TODO: Add tooltips
class Slider(QWidget):
    def __init__(self, caption, default_value, minimum_value=1, maximum_value=60, single_step=1,
            page_step=6, caption_size=None, unit='', time=False):
        QWidget.__init__(self)

        self.value = default_value
        self.unit = unit
        self.time = time

        description = QLabel(caption)
        description.setWordWrap(True)
        if caption_size:
            description.setMaximumWidth(caption_size)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximum(maximum_value)
        self.slider.setMinimum(minimum_value)
        self.slider.setSingleStep(single_step)
        self.slider.setPageStep(page_step)
        #self.slider.setTickInterval(2)
        #self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.valueChanged.connect(self.__on_change)

        self.value_label = QLabel()

        hbox = QHBoxLayout()
        hbox.addWidget(description)
        hbox.addWidget(self.slider)
        hbox.addWidget(self.value_label)
        hbox.setMargin(0)
        self.setLayout(hbox)
        self.setContentsMargins(5, 0, 5, 0)
        self.slider.setValue(self.value)
        self.__on_change(self.value)

    def __on_change(self, value):
        # FIXME: Fill with spaces to reach the maximum length
        self.value = value
        unit = self.unit
        if self.time:
            minutes = timedelta(minutes=self.value)
            date = datetime(1, 1, 1) + minutes
            text = "%02dh %02dm" % (date.hour, date.minute)
        else:
            text = "%s %s" % (self.value, self.unit)
        self.value_label.setText(text)

    def get_value(self):
        return int(self.slider.value())

class CheckBox(QWidget):
    status_changed = pyqtSignal(bool)

    def __init__(self, caption, checked=False):
        QWidget.__init__(self)

        self.value = checked

        self.checkbox = QCheckBox(caption)
        self.checkbox.stateChanged.connect(self.__on_change)

        hbox = QHBoxLayout()
        hbox.addWidget(self.checkbox)
        hbox.setMargin(0)
        self.setLayout(hbox)
        #self.setContentsMargins(5, 0, 5, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.checkbox.setChecked(self.value)

    def __on_change(self, value):
        self.value = value
        if value == Qt.Unchecked:
            self.status_changed.emit(False)
        else:
            self.status_changed.emit(True)

    def get_value(self):
        return self.checkbox.isChecked()

class ComboBox(QWidget):
    def __init__(self, caption, values, default_value, caption_size=None, expand_combo=False):
        QWidget.__init__(self)

        self.values = values

        description = QLabel(caption)
        description.setWordWrap(True)
        if caption_size:
            description.setMaximumWidth(caption_size)

        self.combo = QComboBox()
        for item in values:
            self.combo.addItem(item, item)

        for i in range(0, len(values)):
            if values[i] == default_value:
                self.combo.setCurrentIndex(i)
                break

        hbox = QHBoxLayout()
        hbox.addWidget(description)
        hbox.addSpacing(10)
        if expand_combo:
            hbox.addWidget(self.combo, 1)
        else:
            hbox.addWidget(self.combo)
        hbox.setMargin(0)
        self.setLayout(hbox)
        self.setContentsMargins(0, 0, 0, 0)

    def get_value(self):
        return str(self.values[self.combo.currentIndex()])

class RadioButton(QWidget):
    selected = pyqtSignal()

    def __init__(self, caption, parent, selected=False):
        QWidget.__init__(self)

        self.value = selected
        self.radiobutton = QRadioButton(caption, parent)
        self.radiobutton.clicked.connect(self.__on_change)

        hbox = QHBoxLayout()
        hbox.addWidget(self.radiobutton)
        hbox.setMargin(0)
        self.setLayout(hbox)
        self.setContentsMargins(0, 0, 0, 0)
        self.radiobutton.setChecked(self.value)

    def __on_change(self):
        self.value = True
        self.selected.emit()

    def set_value(self, value):
        self.radiobutton.setChecked(value)

    def get_value(self):
        return self.radiobutton.isChecked()

class PushButton(QWidget):
    clicked = pyqtSignal()

    def __init__(self, caption, button_text, caption_size=None):
        QWidget.__init__(self)

        self.description = QLabel(caption)
        self.description.setWordWrap(True)
        if caption_size:
            self.description.setMaximumWidth(caption_size)

        self.button = QPushButton(i18n.get(button_text))
        self.button.clicked.connect(self.__on_click)

        hbox = QHBoxLayout()
        hbox.addWidget(self.description, 1)
        hbox.addSpacing(10)
        hbox.addWidget(self.button)
        hbox.setMargin(0)
        self.setLayout(hbox)
        self.setContentsMargins(0, 0, 0, 0)

    def __on_click(self):
        self.clicked.emit()

class LineEdit(QWidget):
    def __init__(self, caption, default_value=None, caption_size=None, text_size=None):
        QWidget.__init__(self)

        self.description = QLabel(caption)
        self.description.setWordWrap(True)
        if caption_size:
            self.description.setMaximumWidth(caption_size)

        self.line_edit = QLineEdit()
        if default_value:
            self.line_edit.setText(default_value)
        if text_size:
            self.line_edit.setMaximumWidth(text_size)

        hbox = QHBoxLayout()
        hbox.addWidget(self.description)
        hbox.addSpacing(10)
        hbox.addWidget(self.line_edit)
        if text_size:
            hbox.addStretch(1)
        hbox.setMargin(0)
        self.setLayout(hbox)
        self.setContentsMargins(0, 0, 0, 0)

    def set_visible(self, value):
        self.description.setVisible(value)
        self.line_edit.setVisible(value)

    def get_value(self):
        return str(self.line_edit.text())

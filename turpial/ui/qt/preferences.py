# -*- coding: utf-8 -*-

# Qt preferences dialog for Turpial

from datetime import datetime, timedelta

#from PyQt4.QtGui import QFont
#from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QSlider
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QButtonGroup
from PyQt4.QtGui import QRadioButton
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n

#TODO: Open in a specific tab
class PreferencesDialog(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('preferences'))
        self.setFixedSize(400, 350)
        self.current_config = self.base.get_config()

        self.tabbar = QTabWidget()
        self.tabbar.setTabsClosable(False)
        self.tabbar.setMovable(False)
        self.tabbar.setUsesScrollButtons(True)
        self.tabbar.setElideMode(Qt.ElideNone)

        self.tabbar.addTab(GeneralPage(base), i18n.get('general'))
        self.tabbar.addTab(NotificationsPage(), i18n.get('notifications'))
        self.tabbar.addTab(ServicesPage(base), i18n.get('services'))
        self.tabbar.addTab(BrowserPage(base), i18n.get('web_browser'))
        self.tabbar.addTab(ProxyPage(base), i18n.get('proxy'))
        self.tabbar.addTab(AdvancedPage(base), i18n.get('advanced'))

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
        vbox.setContentsMargins(10, 10, 10, 5)
        self.setLayout(vbox)
        self.show()

    def __on_close(self):
        self.close()

    def __on_save(self):
        print 'saving'
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

        current_frecuency = base.core.get_update_interval()

        self.update_frecuency = Slider(i18n.get('update_frecuency'), unit='min',
            default_value=current_frecuency)
        self.statuses_per_column = Slider(i18n.get('statuses_per_column'), minimum_value=20,
            maximum_value=200, default_value=20)
        self.queue_frecuency = Slider(i18n.get('queue_frecuency'), minimum_value=5,
            maximum_value=720, default_value=20, single_step=15, time=True)
        self.minimize_on_close = CheckBox(i18n.get('minimize_on_close'))

        self.layout.addWidget(self.update_frecuency)
        self.layout.addWidget(self.queue_frecuency)
        self.layout.addWidget(self.statuses_per_column)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.minimize_on_close)
        self.layout.addStretch(1)

    def get_config(self):
        raise NotImplemented

class NotificationsPage(BasePage):
    def __init__(self):
        BasePage.__init__(self, i18n.get('notifications_tab_description'))

        self.notify_on_update = CheckBox(i18n.get('notify_on_update'))
        self.notify_on_actions = CheckBox(i18n.get('notify_on_actions'))
        self.sound_on_login = CheckBox(i18n.get('sound_on_login'))
        self.sound_on_update = CheckBox(i18n.get('sound_on_updates'))

        self.layout.addWidget(self.notify_on_update)
        self.layout.addWidget(self.notify_on_actions)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.sound_on_login)
        self.layout.addWidget(self.sound_on_update)
        self.layout.addStretch(1)

    def get_config(self):
        raise NotImplemented

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
        raise NotImplemented

class BrowserPage(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)

        current_browser = base.core.get_default_browser()

        description = QLabel(i18n.get('web_browser_tab_description'))
        description.setWordWrap(True)

        self.command = QLineEdit()

        if current_browser == '':
            default_value = True
            custom_value = False
            self.command.setText('')
        else:
            default_value = False
            custom_value = True
            self.command.setText(current_browser)

        self.default_browser = RadioButton(i18n.get('use_default_browser'), self,
            selected=default_value)
        self.default_browser.selected.connect(self.__on_defaul_selected)
        self.custom_browser = RadioButton(i18n.get('set_custom_browser'), self,
            selected=custom_value)
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

    def __on_defaul_selected(self):
        self.open_button.setEnabled(False)
        self.command.setEnabled(False)

    def __on_custom_selected(self):
        self.open_button.setEnabled(True)
        self.command.setEnabled(True)

    def get_config(self):
        raise NotImplemented

class ProxyPage(BasePage):
    def __init__(self, base):
        BasePage.__init__(self, i18n.get('proxy_tab_description'))

        default_authenticated = False

        self.protocol = ComboBox(i18n.get('type'), ['HTTP', 'HTTPS'], 'HTTP', expand_combo=True)
        self.host = LineEdit(i18n.get('host'))
        self.port = LineEdit(i18n.get('port'), text_size=100)
        self.authenticated = CheckBox(i18n.get('with_authentication'), checked=default_authenticated)
        self.authenticated.status_changed.connect(self.__on_click_authenticated)
        self.username = LineEdit(i18n.get('username'))
        self.password = LineEdit(i18n.get('password'))

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
        raise NotImplemented

class AdvancedPage(BasePage):
    def __init__(self, base):
        BasePage.__init__(self, i18n.get('advanced_tab_description'))

        clean_cache_caption = "%s\n(%s)" % (i18n.get('delete_all_files_in_cache'), base.get_cache_size())
        self.clean_cache = PushButton(clean_cache_caption, i18n.get('clean_cache'))
        self.clean_cache.clicked.connect(self.__on_clean_cache)
        self.restore_config = PushButton(i18n.get('restore_config_to_default'), i18n.get('restore_config'))
        self.restore_config.clicked.connect(self.__on_config_restore)
        self.socket_timeout = Slider(i18n.get('socket_timeout'), 20, minimum_value=5, maximum_value=120,
            unit='sec')
        self.show_avatars = CheckBox(i18n.get('show_avatars'))

        self.layout.addWidget(self.clean_cache)
        self.layout.addWidget(self.restore_config)
        self.layout.addSpacing(15)
        self.layout.addWidget(self.socket_timeout)
        self.layout.addSpacing(10)
        self.layout.addWidget(self.show_avatars)
        self.layout.addStretch(1)

    def __on_clean_cache(self):
        print 'cleaning cache'
        clean_cache_caption = "%s\n(0 B)" % (i18n.get('delete_all_files_in_cache'))
        self.clean_cache.button.setEnabled(False)
        self.clean_cache.description.setText(clean_cache_caption)

    def __on_config_restore(self):
        print 'restoring config'

    def get_config(self):
        raise NotImplemented


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
        return int(self.slider.getValue())

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
        return self.values[self.combo.currentIndex()]

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

    def get_text(self):
        pass

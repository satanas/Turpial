# -*- coding: utf-8 -*-

# Qt preferences dialog for Turpial

#from PyQt4.QtGui import QFont
#from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QSlider
from PyQt4.QtGui import QTabBar
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QComboBox
from PyQt4.QtGui import QCheckBox
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n
#from turpial.ui.qt.column import StatusesColumn
#from turpial.ui.qt.loader import BarLoadIndicator
#from turpial.ui.qt.widgets import ImageButton, VLine, HLine
#
#from libturpial.common.tools import get_username_from

#TODO: Open in a specific tab
class PreferencesDialog(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('preferences'))
        self.setFixedSize(400, 350)
        self.current_config = self.base.get_config()

        #self.list_ = QListView()
        #self.list_.setResizeMode(QListView.Adjust)
        #self.list_.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        #self.list_.setMaximumWidth(128)
        #self.list_.setGridSize(QSize(-1, 10))
        #self.list_.clicked.connect(self.__on_change_item)
        self.list_ = QTabWidget()
        self.list_.setTabsClosable(False)
        self.list_.setMovable(False)
        self.list_.setUsesScrollButtons(True)
        #self.list_.currentChanged.connect(self.__on_change_item)
        self.list_.addTab(GeneralPage(base), i18n.get('general'))
        self.list_.addTab(NotificationsPage(), i18n.get('notifications'))
        self.list_.addTab(ServicesPage(base), i18n.get('services'))

        #self.pages = QStackedWidget()
        #self.pages.addWidget(GeneralPage(base))
        #self.pages.addWidget(NotificationsPage())
        #self.pages.addWidget(ServicesPage(base))

        #layout = QVBoxLayout()
        #layout.addWidget(self.list_)
        #layout.addWidget(self.pages, 1)

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
        #vbox.addLayout(layout)
        vbox.addWidget(self.list_, 1)
        vbox.addLayout(button_box)
        vbox.setContentsMargins(10, 10, 10, 5)
        self.setLayout(vbox)
        self.show()

    def __on_close(self):
        self.close()

    def __on_save(self):
        print 'saving'
        self.close()

    def __update(self):
        #model = QStandardItemModel()
        #self.list_.setModel(model)
        #for key in ['general', 'notifications', 'services', 'filters', 'web_browser', 'advanced', 'proxy']:
        #    item = QStandardItem(i18n.get(key))
        #    item.setEditable(False)
        #    model.appendRow(item)
        for key in ['general', 'notifications', 'services', 'web_browser', 'proxy', 'advanced']:
            self.list_.addTab(i18n.get(key))
        self.show()


class GeneralPage(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)

        #update_frecuency
        self.update_frecuency = Slider(i18n.get('update_frecuency'), unit='min', default_value=5)
        self.statuses_per_column = Slider(i18n.get('statuses_per_column'), minimum_value=20,
                maximum_value=200, default_value=20)
        self.minimize_on_close = CheckBox(i18n.get('minimize_on_close'))

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 5, 5, 0)
        vbox.addWidget(self.update_frecuency)
        vbox.addWidget(self.statuses_per_column)
        vbox.addWidget(self.minimize_on_close)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def get_config(self):
        raise NotImplemented

class NotificationsPage(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        # Select the notifications you want to receive from turpial
        description = QLabel("Select the notifications you want to receive from Turpial")

        self.notify_on_update = CheckBox(i18n.get('notify_on_update'))
        self.notify_on_actions = CheckBox(i18n.get('notify_on_actions'))
        self.notify_off = CheckBox(i18n.get('turn_off_notifications'))
        self.notify_off.status_changed.connect(self.__on_turn_off_notifications)
        self.sound_on_login = CheckBox(i18n.get('sound_on_login'))
        self.sound_on_update = CheckBox(i18n.get('sound_on_update'))
        self.sound_off = CheckBox(i18n.get('turn_off_sounds'))
        self.sound_off.status_changed.connect(self.__on_turn_off_sounds)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(5, 5, 5, 0)
        vbox.addWidget(description)
        vbox.addSpacing(10)
        vbox.addWidget(self.notify_on_update)
        vbox.addWidget(self.notify_on_actions)
        vbox.addWidget(self.notify_off)
        vbox.addSpacing(15)
        vbox.addWidget(self.sound_on_login)
        vbox.addWidget(self.sound_on_update)
        vbox.addWidget(self.sound_off)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def __on_turn_off_notifications(self, value):
        if value:
            self.notify_on_update.setEnabled(False)
            self.notify_on_actions.setEnabled(False)
        else:
            self.notify_on_update.setEnabled(True)
            self.notify_on_actions.setEnabled(True)

    def __on_turn_off_sounds(self, value):
        if value:
            self.sound_on_login.setEnabled(False)
            self.sound_on_update.setEnabled(False)
        else:
            self.sound_on_login.setEnabled(True)
            self.sound_on_update.setEnabled(True)

    def get_config(self):
        raise NotImplemented

class ServicesPage(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)

        description = QLabel("Select your preferred service to short URLs and upload images")
        description.setWordWrap(True)

        short_url_services = base.core.get_available_short_url_services()
        default_short_url_service = base.core.get_shorten_url_service()
        self.short_url = ComboBox(i18n.get('short_urls'), short_url_services, default_short_url_service)

        upload_media_services = base.core.get_available_upload_media_services()
        default_upload_media_service = base.core.get_upload_media_service()
        self.upload_media = ComboBox(i18n.get('upload_image'), upload_media_services,
            default_upload_media_service)

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(5, 5, 5, 0)
        vbox.addWidget(description)
        vbox.addSpacing(15)
        vbox.addWidget(self.short_url)
        vbox.addWidget(self.upload_media)
        vbox.addStretch(1)

        self.setLayout(vbox)

    def get_config(self):
        raise NotImplemented

################################################################################
### Widgets
################################################################################

# TODO: Add tooltips
class Slider(QWidget):
    def __init__(self, caption, default_value, minimum_value=1, maximum_value=60, single_step=1,
            page_step=6, caption_size=None, unit=''):
        QWidget.__init__(self)

        self.value = default_value
        self.unit = unit

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
        text = "%s %s" % (value, self.unit)
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

        self.value_label = QLabel()

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
    def __init__(self, caption, values, default_value, caption_size=None):
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
        hbox.addWidget(self.combo, 1)
        #hbox.addStretch(1)
        hbox.setMargin(0)
        self.setLayout(hbox)
        self.setContentsMargins(0, 0, 0, 0)

    def get_value(self):
        return self.values[self.combo.currentIndex()]

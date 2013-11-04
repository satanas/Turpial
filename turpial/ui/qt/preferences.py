# -*- coding: utf-8 -*-

# Qt preferences dialog for Turpial

#from PyQt4.QtGui import QFont
#from PyQt4.QtGui import QIcon
#from PyQt4.QtGui import QLabel
#from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QStackedWidget
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItemModel
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

#from PyQt4.QtCore import Qt
from PyQt4.QtCore import QSize
#from PyQt4.QtCore import pyqtSignal
#
from turpial.ui.lang import i18n
#from turpial.ui.qt.column import StatusesColumn
#from turpial.ui.qt.loader import BarLoadIndicator
#from turpial.ui.qt.widgets import ImageButton, VLine, HLine
#
#from libturpial.common.tools import get_username_from


class PreferencesDialog(QWidget):
    def __init__(self, base):
        QWidget.__init__(self)
        self.base = base
        self.setWindowTitle(i18n.get('preferences'))
        self.setFixedSize(500, 400)

        self.list_ = QListView()
        self.list_.setResizeMode(QListView.Adjust)
        self.list_.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.list_.setMaximumWidth(128)
        self.list_.setGridSize(QSize(-1, 10))

        self.pages = QStackedWidget()

        hbox = QHBoxLayout()
        hbox.addWidget(self.list_)
        hbox.addWidget(self.pages, 1)

        self.save_button = QPushButton(i18n.get('save'))
        self.close_button = QPushButton(i18n.get('close'))

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.setSpacing(4)
        button_box.addWidget(self.save_button)
        button_box.addWidget(self.close_button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addLayout(button_box)
        self.setLayout(vbox)
        self.showed = False

    def __update(self):
        self.current_config = self.base.get_config()
        model = QStandardItemModel()
        self.list_.setModel(model)
        for key in ['general', 'notifications', 'services', 'filter', 'browser', 'advanced', 'proxy']:
            item = QStandardItem(i18n.get(key))
            model.appendRow(item)


    def show(self):
        if self.showed:
            return self.raise_()

        self.__update()
        QWidget.show(self)
        self.showed = True

class GenericTab(QWidget):
    def __init__(self, desc, current=None):
        QWidget.__init__(self)

        self.current = current
        description = Gtk.Label()
        description.set_line_wrap(True)
        description.set_use_markup(True)
        description.set_markup(desc)
        description.set_justify(Gtk.Justification.FILL)

        desc_align = Gtk.Alignment(xalign=0.0, yalign=0.0)
        desc_align.set_padding(0, 5, 10, 10)
        desc_align.add(description)

        self._container = Gtk.VBox(False, 2)

        hbox = Gtk.HBox(False, 10)
        hbox.pack_start(self._container, True, True, 10)

        self.pack_start(desc_align, False, False, 5)
        self.pack_start(hbox, True, True, 0)

    def add_child(self, child, expand=True, fill=True, padding=0):
        self._container.pack_start(child, expand, fill, padding)

    def get_config(self):
        raise NotImplemented

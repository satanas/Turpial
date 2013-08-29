# -*- coding: utf-8 -*-

# Qt container for all columns in Turpial

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QListView
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.column import StatusesColumn

class Container(QVBoxLayout):
    def __init__(self, base):
        QVBoxLayout.__init__(self)
        self.base = base
        self.child = None
        self.columns = {}
        self.is_empty = None

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def empty(self, with_accounts=None):
        if self.child:
            self.child.deleteLater()

        image = self.base.load_image('logo.png', True)
        logo = QLabel()
        logo.setPixmap(image)
        logo.setAlignment(Qt.AlignCenter)
        logo.setContentsMargins(0, 80, 0, 0)

        welcome = QLabel()
        welcome.setText(i18n.get('welcome'))
        welcome.setAlignment(Qt.AlignCenter)

        message = QLabel()
        if with_accounts:
            message.setText(i18n.get('add_some_columns'))
        else:
            message.setText(i18n.get('add_new_account'))
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)

        self.child = QVBoxLayout()
        self.child.addWidget(logo, 1)
        self.child.addWidget(welcome)
        self.child.addWidget(message)
        self.child.setSpacing(10)
        self.child.setContentsMargins(30, 0, 30, 60)

        self.insertLayout(0, self.child)
        self.is_empty = True

    def normal(self):
        columns = self.base.core.get_registered_columns()

        if self.child:
            self.clear_layout(self)

        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)

        self.columns = {}
        for column in columns:
            self.columns[column.id_] = StatusesColumn(self.base, column.id_)
            hbox.addWidget(self.columns[column.id_], 1)

        viewport = QWidget()
        viewport.setLayout(hbox)

        self.child = QScrollArea()
        self.child.setWidgetResizable(True)
        self.child.setWidget(viewport)

        self.addWidget(self.child, 1)
        self.is_empty = False

    def start_updating(self, column_id):
        return self.columns[column_id].start_updating()

    def stop_updating(self, column_id, errmsg=None, errtype=None):
        self.columns[column_id].stop_updating()

    def is_updating(self, column_id):
        #return self.columns[column_id].updating
        return False

    def update_column(self, column_id, statuses):
        self.columns[column_id].update_statuses(statuses)
        self.stop_updating(column_id)

    def add_column(self, column_id):
        if self.is_empty:
            self.normal()
        else:
            viewport = self.child.widget()
            hbox = viewport.layout()
            self.columns[column_id] = StatusesColumn(self.base, column_id)
            hbox.addWidget(self.columns[column_id], 1)

    def remove_column(self, column_id):
        self.columns[column_id].deleteLater()
        del self.columns[column_id]

    def mark_status_as_favorite(self, status_id):
        for id_, column in self.columns.iteritems():
            column.mark_status_as_favorite(status_id)

    def unmark_status_as_favorite(self, status_id):
        for id_, column in self.columns.iteritems():
            column.unmark_status_as_favorite(status_id)

    def mark_status_as_repeated(self, status_id):
        for id_, column in self.columns.iteritems():
            column.mark_status_as_repeated(status_id)

    def remove_status(self, status_id):
        for id_, column in self.columns.iteritems():
            column.remove_status(status_id)

    def notify_error(self, column_id, id_, message):
        self.columns[column_id].notify_error(id_, message)

    def notify_success(self, column_id, id_, message):
        self.columns[column_id].notify_success(id_, message)

    def notify_warning(self, column_id, id_, message):
        self.columns[column_id].notify_warning(id_, message)

    def notify_info(self, column_id, id_, message):
        self.columns[column_id].notify_info(id_, message)

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

    def clear_layout(self, layout):
        if layout is not None:
            while self.count():
                item = self.takeAt(0)
                print item
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def empty(self, with_accounts=None):
        if self.child:
            #del(self.child)
            self.clear_layout(self.child)

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

    def normal(self, columns):
        if self.child:
            #del(self.child)
            self.clear_layout(self.child)

        hbox = QHBoxLayout()

        self.columns = {}
        for column in columns:
            self.columns[column.id_] = StatusesColumn(self.base, column.id_)
            hbox.addWidget(self.columns[column.id_], 1)

        #column1 = StatusesColumn(self.base, True)
        #column2 = StatusesColumn(self.base)
        #column3 = StatusesColumn(self.base)

        #hbox.addWidget(column1, 1)
        #hbox.addWidget(column2, 1)
        #hbox.addWidget(column3, 1)

        viewport = QWidget()
        viewport.setLayout(hbox)

        self.child = QScrollArea()
        self.child.setWidgetResizable(True)
        self.child.setWidget(viewport)

        self.addWidget(self.child, 1)

    def start_updating(self, column_id):
        return self.columns[column_id].start_updating()

    def stop_updating(self, column_id, errmsg=None, errtype=None):
        self.columns[column_id].stop_updating()

    def is_updating(self, column_id):
        #return self.columns[column_id].updating
        return False

    def update_column(self, column_id, statuses):
        self.columns[column_id].update(statuses)
        self.stop_updating(column_id)

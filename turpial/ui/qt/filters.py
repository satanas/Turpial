# -*- coding: utf-8 -*-

# Qt filters dislog for Turpial

from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout

from turpial.ui.lang import i18n

from turpial.ui.qt.widgets import Window


class FiltersDialog(Window):
    def __init__(self, base):
        Window.__init__(self, base, i18n.get('filters'))
        self.setFixedSize(280, 360)

        self.expression = QLineEdit()
        self.expression.returnPressed.connect(self.__new_filter)

        self.new_button = QPushButton(i18n.get('add_filter'))
        self.new_button.setToolTip(i18n.get('create_a_new_filter'))
        self.new_button.clicked.connect(self.__new_filter)

        expression_box = QHBoxLayout()
        expression_box.addWidget(self.expression)
        expression_box.addWidget(self.new_button)

        self.list_ = QListWidget()
        self.list_.clicked.connect(self.__filter_clicked)

        self.delete_button = QPushButton(i18n.get('delete'))
        self.delete_button.setEnabled(False)
        self.delete_button.setToolTip(i18n.get('delete_selected_filter'))
        self.delete_button.clicked.connect(self.__delete_filter)

        self.clear_button = QPushButton(i18n.get('delete_all'))
        self.clear_button.setEnabled(False)
        self.clear_button.setToolTip(i18n.get('delete_all_filters'))
        self.clear_button.clicked.connect(self.__delete_all)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(self.clear_button)
        button_box.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addLayout(expression_box)
        layout.addWidget(self.list_, 1)
        layout.addLayout(button_box)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 0)
        self.setLayout(layout)
        self.__update()
        self.show()

    def __update(self):
        row = 0
        self.expression.setText('')
        self.list_.clear()
        for expression in self.base.core.list_filters():
            self.list_.addItem(expression)
            row += 1

        self.__enable(True)
        self.delete_button.setEnabled(False)
        if row == 0:
            self.clear_button.setEnabled(False)
        self.expression.setFocus()

    def __filter_clicked(self, point):
        self.delete_button.setEnabled(True)
        self.clear_button.setEnabled(True)

    def __new_filter(self):
        expression = str(self.expression.text())
        self.list_.addItem(expression)
        self.__save_filters()

    def __delete_filter(self):
        self.list_.takeItem(self.list_.currentRow())
        self.__save_filters()

    def __delete_all(self):
        self.__enable(False)
        message = i18n.get('clear_filters_confirm')
        confirmation = self.base.show_confirmation_message(i18n.get('confirm_delete'),
            message)
        if not confirmation:
            self.__enable(True)
            return
        self.list_.clear()
        self.__save_filters()

    def __enable(self, value):
        self.list_.setEnabled(value)
        self.delete_button.setEnabled(value)
        self.clear_button.setEnabled(value)

    def __save_filters(self):
        filters = []
        for i in range(self.list_.count()):
            filters.append(str(self.list_.item(i).text()))
        self.base.save_filters(filters)
        self.__update()

# -*- coding: utf-8 -*-

# Qt status queue for Turpial

import time

from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QTableView
from PyQt4.QtGui import QHeaderView
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QAbstractItemView
from PyQt4.QtGui import QStandardItem
from PyQt4.QtGui import QStandardItemModel

from PyQt4.QtCore import Qt
from PyQt4.QtCore import QTimer
from PyQt4.QtCore import QString

from turpial.ui.lang import i18n
from turpial.ui.util import humanize_time_intervals
from turpial.ui.qt.widgets import Window

from libturpial.common.tools import get_protocol_from, get_username_from


class QueueDialog(Window):
    def __init__(self, base):
        Window.__init__(self, base, i18n.get('messages_queue'))
        self.setFixedSize(500, 400)
        self.last_timestamp = None
        self.showed = False

        self.list_ = QTableView()
        self.list_.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list_.clicked.connect(self.__account_clicked)

        self.caption = QLabel()
        self.caption.setWordWrap(True)
        self.caption.setAlignment(Qt.AlignCenter)

        self.estimated_time = QLabel()
        self.estimated_time.setWordWrap(True)
        self.estimated_time.setAlignment(Qt.AlignCenter)

        self.delete_button = QPushButton(i18n.get('delete'))
        self.delete_button.setEnabled(False)
        self.delete_button.setToolTip(i18n.get('delete_selected_message'))
        self.delete_button.clicked.connect(self.__delete_message)

        self.clear_button = QPushButton(i18n.get('delete_all'))
        self.clear_button.setEnabled(False)
        self.clear_button.setToolTip(i18n.get('delete_all_messages_in_queue'))
        self.clear_button.clicked.connect(self.__delete_all)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(self.clear_button)
        button_box.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.list_, 1)
        layout.addWidget(self.caption)
        layout.addWidget(self.estimated_time)
        layout.addLayout(button_box)
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

    def __account_clicked(self, point):
        self.delete_button.setEnabled(True)
        self.clear_button.setEnabled(True)

    def __delete_message(self):
        self.__disable()
        selection = self.list_.selectionModel()
        index = selection.selectedIndexes()[0]
        message = i18n.get('delete_message_from_queue_confirm')
        confirmation = self.base.show_confirmation_message(i18n.get('confirm_delete'),
            message)
        if not confirmation:
            self.__enable()
            return
        self.base.delete_message_from_queue(index.row())

    def __delete_all(self):
        self.__disable()
        message = i18n.get('clear_message_queue_confirm')
        confirmation = self.base.show_confirmation_message(i18n.get('confirm_delete'),
            message)
        if not confirmation:
            self.__enable()
            return
        self.base.clear_queue()


    def __enable(self):
        self.list_.setEnabled(True)
        self.delete_button.setEnabled(False)
        if len(self.base.core.list_statuses_queue()) > 0:
            self.clear_button.setEnabled(True)
        else:
            self.clear_button.setEnabled(False)

    def __disable(self):
        self.list_.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.clear_button.setEnabled(False)

    def __on_timeout(self):
        now = int(time.time())
        interval = self.base.core.get_queue_interval() * 60
        if self.last_timestamp:
            est_time = ((self.last_timestamp + interval) - now) / 60
        else:
            est_time = 0

        humanized_est_time = humanize_time_intervals(est_time)
        next_message = ' '.join([i18n.get('next_message_should_be_posted_in'), humanized_est_time])

        if len(self.base.core.list_statuses_queue()) == 0:
            self.estimated_time.setText('')
        else:
            self.estimated_time.setText(next_message)

    def start(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.__on_timeout)
        self.timer.start(60000)

    def closeEvent(self, event=None):
        if event:
            event.ignore()
        self.hide()
        self.showed = False

    def show(self):
        if self.showed:
            self.raise_()
            return

        self.update()
        Window.show(self)
        self.showed = True

    def update(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderItem(0, QStandardItem(i18n.get('account')))
        model.setHorizontalHeaderItem(1, QStandardItem(i18n.get('message')))
        self.list_.setModel(model)

        now = int(time.time())
        interval = self.base.core.get_queue_interval() * 60
        if self.last_timestamp:
            est_time = ((self.last_timestamp + interval) - now) / 60
        else:
            est_time = 0

        row = 0
        for status in self.base.core.list_statuses_queue():
            username = get_username_from(status.account_id)
            protocol_image = "%s.png" % get_protocol_from(status.account_id)
            item = QStandardItem(QString.fromUtf8(username))
            item.setIcon(QIcon(self.base.load_image(protocol_image, True)))
            model.setItem(row, 0, item)
            model.setItem(row, 1, QStandardItem(QString.fromUtf8(status.text)))
            row += 1

        humanized_interval = humanize_time_intervals(self.base.core.get_queue_interval())
        humanized_est_time = humanize_time_intervals(est_time)

        warning = i18n.get('messages_will_be_send') % humanized_interval
        next_message = ' '.join([i18n.get('next_message_should_be_posted_in'), humanized_est_time])
        self.caption.setText(warning)

        if row == 0:
            self.estimated_time.setText('')
        else:
            self.estimated_time.setText(next_message)

        self.list_.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.list_.resizeColumnsToContents()

        self.__enable()

    def update_timestamp(self):
        if len(self.base.core.list_statuses_queue()) > 0:
            self.last_timestamp = int(time.time())
        else:
            self.last_timestamp = None

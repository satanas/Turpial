# -*- coding: utf-8 -*-

# Qt container for all columns in Turpial

from PyQt4.QtCore import Qt

from PyQt4.QtGui import QFont
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QCursor
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QScrollArea
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout

from turpial.ui.lang import i18n
from turpial.ui.qt.column import StatusesColumn
from turpial.ui.qt.widgets import BarLoadIndicator

from libturpial.common import OS_MAC
from libturpial.common.tools import detect_os

class Container(QVBoxLayout):
    def __init__(self, base):
        QVBoxLayout.__init__(self)
        self.base = base
        self.child = None
        self.columns = {}
        self.is_empty = None
        self.column_indexes = []
        self.focus_index = 0
        self.loading()

    def __link_clicked(self, url):
        if url == 'cmd:add_columns':
            self.base.show_column_menu(QCursor.pos())
        elif url == 'cmd:add_accounts':
            self.base.show_accounts_dialog()
        elif url == 'cmd:restart':
            self.base.restart()

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
            self.clear_layout(self)

        image = self.base.load_image('turpial-196.png', True)
        logo = QLabel()
        logo.setPixmap(image)
        logo.setAlignment(Qt.AlignCenter)
        logo.setContentsMargins(0, 80, 0, 0)

        appname = QLabel('Turpial 3')
        if detect_os() == OS_MAC:
            font = QFont('Maven Pro Light', 28, 0, False)
            font2 = QFont('Ubuntu', 16, 0, False)
        else:
            font = QFont('Maven Pro Light', 18, QFont.Light, False)
            font2 = QFont('Ubuntu', 12, QFont.Normal, False)
        appname.setFont(font)

        welcome = QLabel()
        welcome.setText(i18n.get('welcome'))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(font)

        message = QLabel()
        if with_accounts:
            text = "%s <a href='cmd:add_columns'>%s</a>" % (i18n.get('you_have_accounts_registered'),
                i18n.get('add_some_columns'))
        else:
            text = "<a href='cmd:add_accounts'>%s</a> %s" % (i18n.get('add_new_account'),
                i18n.get('to_start_using_turpial'))
        message.setText(text)
        message.linkActivated.connect(self.__link_clicked)
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setFont(font2)

        self.child = QVBoxLayout()
        self.child.addWidget(logo)
        self.child.addWidget(welcome)
        self.child.setSpacing(10)
        self.child.addWidget(message)
        self.child.setSpacing(10)
        self.child.setContentsMargins(30, 0, 30, 60)

        self.insertLayout(0, self.child)
        self.is_empty = True

    def loading(self):
        if self.child:
            self.clear_layout(self)

        image = self.base.load_image('turpial-196.png', True)
        logo = QLabel()
        logo.setPixmap(image)
        logo.setAlignment(Qt.AlignCenter)
        logo.setContentsMargins(0, 80, 0, 0)

        appname = QLabel('Turpial 3')
        if detect_os() == OS_MAC:
            font = QFont('Maven Pro Light', 28, 0, False)
            font2 = QFont('Ubuntu', 16, 0, False)
        else:
            font = QFont('Maven Pro Light', 18, QFont.Light, False)
            font2 = QFont('Ubuntu', 12, QFont.Normal, False)
        appname.setFont(font)

        welcome = QLabel()
        welcome.setText(i18n.get('hi_there'))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(font)

        message = QLabel()
        message.setText(i18n.get('give_me_a_minute'))
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setFont(font2)

        loader = BarLoadIndicator(None)

        self.child = QVBoxLayout()
        self.child.addWidget(logo)
        self.child.addWidget(welcome)
        self.child.addSpacing(10)
        self.child.addWidget(message)
        #self.child.setSpacing(10)
        self.child.addStretch(1)
        self.child.addWidget(loader)
        self.child.setContentsMargins(30, 0, 30, 30)

        self.insertLayout(0, self.child)
        self.is_empty = True

    def error(self):
        if self.child:
            self.clear_layout(self)

        image = self.base.load_image('turpial-196.png', True)
        logo = QLabel()
        logo.setPixmap(image)
        logo.setAlignment(Qt.AlignCenter)
        logo.setContentsMargins(0, 80, 0, 0)

        appname = QLabel('Turpial 3')
        if detect_os() == OS_MAC:
            font = QFont('Maven Pro Light', 28, 0, False)
            font2 = QFont('Ubuntu', 16, 0, False)
        else:
            font = QFont('Maven Pro Light', 18, QFont.Light, False)
            font2 = QFont('Ubuntu', 12, QFont.Normal, False)
        appname.setFont(font)

        welcome = QLabel()
        welcome.setText(i18n.get('oh_oh'))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setFont(font)

        message = QLabel()
        text = "%s. <a href='cmd:restart'>%s</a>" % (i18n.get('something_terrible_happened'),
            i18n.get('try_again'))
        message.setText(text)
        message.linkActivated.connect(self.__link_clicked)
        message.setAlignment(Qt.AlignCenter)
        message.setWordWrap(True)
        message.setFont(font2)

        self.child = QVBoxLayout()
        self.child.addWidget(logo)
        self.child.addWidget(welcome)
        self.child.addSpacing(10)
        self.child.addWidget(message)
        #self.child.setSpacing(10)
        self.child.addStretch(1)
        self.child.setContentsMargins(30, 0, 30, 30)

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
            self.column_indexes.append(column.id_)
            self.columns[column.id_] = StatusesColumn(self.base, column.id_)
            hbox.addWidget(self.columns[column.id_], 1)

        viewport = QWidget()
        viewport.setLayout(hbox)

        self.child = QScrollArea()
        self.child.setWidgetResizable(True)
        self.child.setWidget(viewport)

        self.addWidget(self.child, 1)
        self.is_empty = False
        self.columns[self.column_indexes[self.focus_index]].webview.setFocus()

    def start_updating(self, column_id):
        return self.columns[column_id].start_updating()

    def stop_updating(self, column_id, errmsg=None, errtype=None):
        self.columns[column_id].stop_updating()

    def is_updating(self, column_id):
        return self.columns[column_id].updating

    def update_timestamps(self, column_id):
        self.columns[column_id].update_timestamps()
        self.stop_updating(column_id)

    def update_column(self, column_id, statuses):
        if column_id not in self.columns:
            return
        self.columns[column_id].update_statuses(statuses)
        self.stop_updating(column_id)
        self.base.add_extra_friends_from_statuses(statuses)

    def add_column(self, column_id):
        if self.is_empty:
            self.normal()
        else:
            viewport = self.child.widget()
            hbox = viewport.layout()
            self.columns[column_id] = StatusesColumn(self.base, column_id)
            self.column_indexes.append(column_id)
            hbox.addWidget(self.columns[column_id], 1)

    def remove_column(self, column_id):
        self.columns[column_id].deleteLater()
        self.column_indexes.remove(column_id)
        del self.columns[column_id]

    def mark_status_as_favorite(self, status_id):
        for id_, column in self.columns.iteritems():
            column.mark_status_as_favorite(status_id)
            column.release_status(status_id)

    def unmark_status_as_favorite(self, status_id):
        for id_, column in self.columns.iteritems():
            column.unmark_status_as_favorite(status_id)
            column.release_status(status_id)

    def mark_status_as_repeated(self, status_id):
        for id_, column in self.columns.iteritems():
            column.mark_status_as_repeated(status_id)
            column.release_status(status_id)

    def remove_status(self, status_id):
        for id_, column in self.columns.iteritems():
            column.remove_status(status_id)

    def update_conversation(self, status, column_id, status_root_id):
        for id_, column in self.columns.iteritems():
            if id_ == column_id:
                column.update_conversation(status, status_root_id)

    def error_loading_conversation(self, column_id, status_root_id, response=None):
        for id_, column in self.columns.iteritems():
            if id_ == column_id:
                column.error_in_conversation(status_root_id)
        message = self.base.get_error_message_from_response(response, i18n.get('error_loading_conversation'))
        self.notify_error(column_id, self.base.random_id(), message)

    def error_updating_column(self, column_id, response=None):
        self.stop_updating(column_id)
        message = self.base.get_error_message_from_response(response, i18n.get('error_updating_column'))
        self.notify_error(column_id, self.base.random_id(), message)

    def error_repeating_status(self, column_id, status_id, response=None):
        for id_, column in self.columns.iteritems():
            column.release_status(status_id)
        message = self.base.get_error_message_from_response(response, i18n.get('error_repeating_status'))
        self.notify_error(column_id, status_id, message)

    def error_deleting_status(self, column_id, status_id, response=None):
        for id_, column in self.columns.iteritems():
            column.release_status(status_id)
        message = self.base.get_error_message_from_response(response, i18n.get('error_deleting_status'))
        self.notify_error(column_id, status_id, message)

    def error_marking_status_as_favorite(self, column_id, status_id, response=None):
        for id_, column in self.columns.iteritems():
            column.release_status(status_id)
        message = self.base.get_error_message_from_response(response, i18n.get('error_marking_status_as_favorite'))
        self.notify_error(column_id, status_id, message)

    def error_unmarking_status_as_favorite(self, column_id, status_id, response=None):
        for id_, column in self.columns.iteritems():
            column.release_status(status_id)
        message = self.base.get_error_message_from_response(response, i18n.get('error_unmarking_status_as_favorite'))
        self.notify_error(column_id, status_id, message)

    def notify_error(self, column_id, id_, message):
        self.columns[str(column_id)].notify_error(id_, message)

    def notify_success(self, column_id, id_, message):
        self.columns[str(column_id)].notify_success(id_, message)

    def notify_warning(self, column_id, id_, message):
        self.columns[str(column_id)].notify_warning(id_, message)

    def notify_info(self, column_id, id_, message):
        self.columns[str(column_id)].notify_info(id_, message)

    def focusWidget(self):
        if len(self.columns) == 0:
            return None
        else:
            return self.columns[self.column_indexes[self.focus_index]]

    def nextInFocusChain(self):
        self.focus_index += 1
        if self.focus_index >= len(self.columns):
            self.focus_index = 0
        return self.columns[self.column_indexes[self.focus_index]]

    def previousInFocusChain(self):
        self.focus_index -= 1
        if self.focus_index < 0:
            self.focus_index = len(self.columns) - 1
        return self.columns[self.column_indexes[self.focus_index]]

    def load_style(self):
        for id_, column in self.columns.iteritems():
            column.load_style()

    def redraw(self):
        for id_, column in self.columns.iteritems():
            column.redraw()

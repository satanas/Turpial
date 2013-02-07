# -*- coding: utf-8 -*-

# Qt container for all columns in Turpial

from PyQt4 import QtGui

from turpial.ui.lang import i18n

class Container(QtGui.QVBoxLayout):
    def __init__(self, base):
        QtGui.QVBoxLayout.__init__(self)
        self.base = base
        self.child = None
        self.columns = {}

    def empty(self):
        if self.child:
            self.removeWidget(self.child)

        #placeholder = QImage()

        image = self.base.load_image('logo.png', True)
        label = QtGui.QLabel()
        label.setPixmap(image)

        welcome = QtGui.QLabel()
        #welcome.set_use_markup(True)
        welcome.setText(i18n.get('welcome'))

        #no_accounts = Gtk.Label()
        #no_accounts.set_use_markup(True)
        #no_accounts.set_line_wrap(True)
        #no_accounts.set_justify(Gtk.Justification.CENTER)
        #if len(self.base.get_accounts_list()) > 0:
        #    no_accounts.set_markup(i18n.get('no_registered_columns'))
        #else:
        #    no_accounts.set_markup(i18n.get('no_active_accounts'))

        self.child = QtGui.QVBoxLayout()
        self.child.addStretch(1)
        #self.child.pack_start(placeholder, False, False, 40)
        self.child.addWidget(label)
        self.child.addWidget(welcome)
        #self.child.pack_start(no_accounts, False, False, 0)


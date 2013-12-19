# -*- coding: utf-8 -*-

""" Widget to make the OAuth dance from Turpial"""
#
# Author: Wil Alvarez (aka Satanas)

from gi.repository import Gtk
from gi.repository import GObject

from turpial.ui.lang import i18n
from turpial.ui.gtk.htmlview import HtmlView

DELETE_COOKIES_SCRIPT = """
function delete_cookies() {
    var cookies = document.cookie.split(';');
    for (var i=0; i<cookies.length; i++) {
        var cookie = cookies[i];
        console.log(cookie);
    }
}
delete_cookies();
"""

class OAuthDialog(Gtk.Window):
    __gsignals__ = {
        "response": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_STRING,)),
        "cancel": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_STRING,)),
    }

    def __init__(self, mainwin, parent, account_id):
        Gtk.Window.__init__(self)

        self.account_id = account_id
        self.mainwin = mainwin
        self.set_title(i18n.get('secure_auth'))
        self.set_default_size(800, 550)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.connect('delete-event', self.__cancel)

        self.view = HtmlView()
        self.view.connect('load-started', self.__started)
        self.view.connect('load-finished', self.__finished)

        self.label = Gtk.Label()
        self.label.set_use_markup(True)
        self.label.set_alignment(0, 0)
        self.label.set_markup(i18n.get('authorize_turpial'))

        self.waiting_label = Gtk.Label()
        self.waiting_label.set_use_markup(True)
        self.waiting_label.set_alignment(1.0, 0.0)

        self.spinner = Gtk.Spinner()

        lblbox = Gtk.HBox(False, 2)
        lblbox.pack_start(self.label, True, True, 2)
        lblbox.pack_start(self.waiting_label, True, True, 2)
        lblbox.pack_start(self.spinner, False, False, 2)

        self.pin = Gtk.Entry()
        cancel = Gtk.Button(stock=Gtk.STOCK_CANCEL)
        cancel.set_size_request(80, 0)
        accept = Gtk.Button(stock=Gtk.STOCK_OK)
        accept.set_size_request(80, 0)
        accept.set_can_default(True)
        accept.grab_default()

        hbox = Gtk.HBox(False, 0)
        hbox.pack_start(self.pin, True, True, 2)
        hbox.pack_start(cancel, False, False, 2)
        hbox.pack_start(accept, False, False, 2)

        vbox = Gtk.VBox(False, 5)
        vbox.pack_start(self.view, True, True, 0)
        vbox.pack_start(lblbox, False, False, 2)
        vbox.pack_start(hbox, False, False, 2)
        vbox.set_property('margin', 10)

        self.pin.connect('activate', self.__accept)
        cancel.connect('clicked', self.__cancel)
        accept.connect('clicked', self.__accept)

        self.add(vbox)
        self.show_all()

    def __cancel(self, widget, event=None):
        self.quit()

    def __accept(self, widget):
        verifier = self.pin.get_text()
        if verifier == '':
            return

        self.quit(verifier)

    def __started(self, widget):
        self.spinner.start()
        self.waiting_label.set_markup(i18n.get('loading'))

    def __finished(self, widget):
        self.spinner.stop()
        self.spinner.hide()
        self.waiting_label.set_markup('')

    def open(self, uri):
        self.view.execute(DELETE_COOKIES_SCRIPT);
        self.view.load(uri)
        self.show_all()
        self.__started(None)

    def quit(self, response=None):
        self.view.stop()
        if response:
            self.emit('response', response, self.account_id)
        else:
            self.emit('cancel', 'login_cancelled', self.account_id)
        self.destroy()


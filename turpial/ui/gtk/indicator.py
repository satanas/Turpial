# -*- coding: utf-8 -*-

""" Indicator module for Turpial """
#
# Author: Wil Alvarez (aka Satanas)

import os
import logging

from gi.repository import GObject

from turpial.ui.lang import i18n

log = logging.getLogger('Indicator')

INDICATOR = True

try:
    from gi.repository import Indicate
except ImportError, exc:
    log.info('Could not import Indicate module. Support for indicators disabled')
    INDICATOR = False

class Indicators(GObject.GObject):
    __gsignals__ = {
        "main-clicked": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ()),
        "indicator-clicked": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, )),
    }

    def __init__(self, disable=False):
        GObject.GObject.__init__(self)
        self.indicators = {}
        self.activate()
        self.disable = disable

        if not INDICATOR:
            log.debug('Module not available')
            self.disable = True
            return

        if disable:
            log.debug('Module disabled')
            return

        desktop_file = os.path.join(os.getcwd(), "turpial.desktop")

        server = indicate.indicate_server_ref_default()
        server.set_type("message.micro")
        server.set_desktop_file(desktop_file)
        server.show()

        server.connect("server-display", self.__on_server_display)

    def __on_server_display(self, server, data):
        self.emit('main-clicked')

    def __on_user_display(self, indicator, data):
        self.emit('indicator-clicked', indicator)

    def toggle_activation(self):
        if self.active:
            self.active = False
        else:
            self.active = True

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def add_update(self, column, count):
        if self.disable:
            log.debug('Module disabled. Adding no indicators')
            return

        global INDICATOR
        if self.active and INDICATOR:
            message = "%s :: %s (%s)" % (column.account_id.split('-')[0],
                column.column_name, i18n.get(column.protocol_id))

            indicator = indicate.Indicator()
            indicator.connect("user-display", self.__on_user_display)
            indicator.set_property("name", message)
            indicator.set_property("count", str(count))
            indicator.label = message
            self.indicators[message] = indicator
            self.indicators[message].show()

    def clean(self):
        for key, indicator in self.indicators.iteritems():
            print indicator
            indicator.hide()

GObject.type_register(Indicators)

# -*- coding: utf-8 -*-

# Widget for HTML view in Turpial
#
# Author: Wil Alvarez (aka Satanas)

import os

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import WebKit
from gi.repository import GObject

class HtmlView(Gtk.VBox):
    __gsignals__ = {
        "action-request": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
        "link-request": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
        "load-started": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ()),
        "load-finished": (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, coding='utf-8'):
        Gtk.VBox.__init__(self, False)

        self.coding = coding
        self.uri = 'file://' + os.path.dirname(__file__)

        self.settings = WebKit.WebSettings()

        self.settings.set_property('enable-default-context-menu', False)
        self.settings.set_property('enable-developer-extras', True)
        self.settings.set_property('enable-plugins', True)
        self.settings.set_property('enable-java_applet', False)
        self.settings.set_property('enable-page-cache', True)
        self.settings.set_property('enable-file-access-from-file-uris', True)
        self.settings.set_property('enable-offline-web-application_cache', False)
        self.settings.set_property('enable-html5-local-storage', False)
        self.settings.set_property('enable-html5-database', False)
        self.settings.set_property('enable-xss-auditor', False)
        try:
            self.settings.set_property('enable-dns-prefetching', False)
        except TypeError:
            pass
        self.settings.set_property('enable-caret-browsing', False)
        self.settings.set_property('resizable-text-areas', False)
        self.settings.web_security_enabled = False

        try:
            self.settings.set_property('enable-accelerated-compositing', True)
        except TypeError:
            print "No support for accelerated compositing"

        self.view = WebKit.WebView()
        self.view.set_settings(self.settings)

        #Added new properties in this way cause 'from' is recognized as a key word
        self.view.get_settings().set_property('enable-universal-access-from-file-uris', True)

        self.view.connect('load-started', self.__started)
        self.view.connect('load-finished', self.__finished)
        self.view.connect('console-message', self.__console_message)
        self.view.connect('navigation-policy-decision-requested', self.__process)
        self.view.connect('new-window-policy-decision-requested', self.__on_new_window_requested);

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        scroll.set_shadow_type(Gtk.ShadowType.IN)
        scroll.add(self.view)

        self.pack_start(scroll, True, True, 0)

    def __on_new_window_requested(self, view, frame, request, decision, u_data):
        self.emit('link-request', request.get_uri())

    def __console_message(self, view, message, line, source_id, data=None):
        #print "%s <%s:%i>" % (message, source_id, line)
        print "%s" % message
        return True

    def __process(self, view, frame, request, action, policy, data=None):
        url = request.get_uri()
        if url is None:
            pass
        elif url.startswith('cmd:'):
            policy.ignore()
            self.emit('action-request', url[4:])
        elif url.startswith('link:'):
            policy.ignore()
            self.emit('link-request', url[5:])
        policy.use()

    def __started(self, widget, frame):
        self.emit('load-started')

    def __finished(self, widget, frame):
        self.emit('load-finished')

    def load(self, url):
        GLib.idle_add(self.view.load_uri, url)

    def render(self, html):
        GLib.idle_add(self.view.load_string, html, "text/html", self.coding, self.uri)

    def execute(self, script):
        script = script.replace('\n', ' ')
        self.view.execute_script(script)

    def stop(self):
        self.view.stop_loading()

GObject.type_register(HtmlView)

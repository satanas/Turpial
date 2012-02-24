# -*- coding: utf-8 -*-

# UnityLauncher to integrate Turpial in Unity
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# Feb 22, 2012

import gobject
import dbus, dbus.service
from dbus.mainloop.glib import DBusGMainLoop

class UnityDBusController(dbus.service.Object):
    def __init__(self, app_uri):
        dbus.service.Object.__init__(self, dbus.SessionBus(), '/')
        self.properties = {}
        self.app_uri = app_uri
        self._update()

    def set_property(self, property_, value):
        if property_ == "count":
            value = dbus.Int64(value)
        self.properties[property_] = value
        self._update()

    def _update(self):
        self.Update(self.app_uri, self.properties)

    @dbus.service.signal(dbus_interface='com.canonical.Unity.LauncherEntry',
                         signature=("sa{sv}"))
    def Update(self, app_uri, properties):
        pass

    @dbus.service.method(dbus_interface='com.canonical.Unity.LauncherEntry',
                         in_signature="", out_signature="sa{sv}")
    def Query(self):
        return self.app_uri, self.properties

class NullUnityDBusController(object):

    def set_property(self, property_, value):
        pass

class UnityLauncher(object):
    def __init__ (self, app_url):
        self.count = 0
        self.dbus_loop = DBusGMainLoop(set_as_default=True)
        app_uri = ""
        if not app_url.startswith("application://"):
            app_uri = "application://%s" % app_url

        try:
            self.launcher = UnityDBusController(app_uri)
        except dbus.exceptions.DBusException:
            self.launcher = NullUnityDBusController()

    def set_count(self, count):
        self.count = count
        self.launcher.set_property("count", self.count)
        self.launcher.set_property("urgent", True)

    def increment_count(self, count):
        self.count += count
        self.launcher.set_property("count", self.count)
        self.launcher.set_property("urgent", True)

    def get_count(self):
        return self.count

    def set_count_visible(self, visible):
        self.launcher.set_property("count-visible", visible)




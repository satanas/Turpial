# -*- coding: utf-8 -*-

# UnityLauncher to integrate Turpial in Unity
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# Feb 22, 2012

try:
    import dbus
    from dbus.mainloop.glib import DBusGMainLoop
    import_success = True
except ImportError:
    import_success = False

BUS_NAME = "org.turpial.ve"
CONTROLLER_OBJ_PATH = "/org/turpial/ve/turpialunity"

class NoneUnityDBusController(object):

    def __init__ (self):
        pass

    def onSignalReceived(self, label_selected):
        pass

    def set_count(self, count):
        pass

    def increment_count(self, count):
        pass

    def get_count(self):
        pass

    def set_count_visible(self, visible):
        pass

    def add_quicklist_button(self, callback, label, visible):
        pass

    def add_quicklist_checkbox(self, callback, label, visible, status):
        pass

    def is_supported(self):
        return False

    def quit(self):
        pass

class UnityLauncher(object):

    def __init__ (self):
        self.dbus_loop = DBusGMainLoop(set_as_default=True)
        self.count = 0
        self.callbacks = {}
        self.bus = dbus.SessionBus(mainloop=self.dbus_loop)
        self.service = self.bus.get_object(BUS_NAME, CONTROLLER_OBJ_PATH)
        self.service.connect_to_signal("buttonPressed", self.onButtonPressed)
        self.service.connect_to_signal("checkChanged", self.onCheckChanged)

    def onButtonPressed(self, label_selected):
        self.callbacks[label_selected]()

    def onCheckChanged(self, label_selected, value):
        self.callbacks[label_selected](value)

    def set_count(self, count):
        self.count = count
        self.service.set_count(self.count)

    def increment_count(self, count):
        self.count += count
        self.set_count(self.count)

    def get_count(self):
        return self.count

    def set_count_visible(self, visible):
        self.service.set_count_visible(visible)

    def add_quicklist_button(self, callback, label, visible):
        self.service.add_quicklist_button(label, visible)
        self.callbacks[label] = callback

    def add_quicklist_checkbox(self, callback, label, visible, status):
        self.service.add_quicklist_checkbox(label, visible, status)
        self.callbacks[label] = callback

    def is_supported(self):
        return True

    def quit(self):
        self.service.quit()
        self.bus.close()

class UnityLauncherFactory:

    def create(self):
        if not import_success:
            return NoneUnityDBusController()
        try:
            return UnityLauncher()
        except dbus.exceptions.DBusException:
            return NoneUnityDBusController()

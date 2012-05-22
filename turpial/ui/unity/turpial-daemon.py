#!/usr/bin/env python

# -*- coding: utf-8 -*-

# TurpialUnityDaemon a separate process to launch to use unity API without conflicts
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# May 22, 2012

from daemon import Daemon
from gi.repository import Unity, GObject, Dbusmenu
import dbus, dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys

BUS_NAME = "org.turpial.ve"
CONTROLLER_OBJ_PATH = "/org/turpial/ve/turpialunity"

class TurpialUnity(dbus.service.Object):

    def __init__(self, loop):
        self.loop = loop
        bus = dbus.service.BusName(BUS_NAME, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus, CONTROLLER_OBJ_PATH)
        self.launcher = Unity.LauncherEntry.get_for_desktop_id("turpial.desktop")
        self.ql = Dbusmenu.Menuitem.new()

    @dbus.service.method(BUS_NAME)
    def set_count(self, count):
        self.launcher.set_property("count", count)

    @dbus.service.method(BUS_NAME)
    def set_count_visible(self, visible):
        self.launcher.set_property("count_visible", visible)
        
    @dbus.service.method(BUS_NAME)
    def add_quicklist_item(self, label, visible):

        def _windowQuit(arg1, arg2, arg3):
            self.launchSignal(label)

        item = Dbusmenu.Menuitem.new()
        item.property_set(Dbusmenu.MENUITEM_PROP_LABEL, label)
        item.property_set_bool(Dbusmenu.MENUITEM_PROP_VISIBLE, visible)
        item.connect("item-activated", _windowQuit, None)
        self.ql.child_append(item)
        self.launcher.set_property("quicklist", self.ql)

    @dbus.service.method(BUS_NAME)
    def quit(self):
        self.loop.quit()

    @dbus.service.signal(BUS_NAME)
    def launchSignal(self, signal):
        pass

 
class TurpialUnityDaemon(Daemon):

    def __init__(self, path):
        Daemon.__init__(self, path)
        self.mainloop = None
        self.service = None

    def stop(self):
        Daemon.stop(self)

    def run(self):
        DBusGMainLoop(set_as_default=True)
        loop = GObject.MainLoop()
        self.service = TurpialUnity(loop)
        loop.run()
 
if __name__ == "__main__":

    daemon = TurpialUnityDaemon('/tmp/turpial-unity-daemon.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

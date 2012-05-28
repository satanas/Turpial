#!/usr/bin/env python

# -*- coding: utf-8 -*-

# TurpialUnityDaemon a separate process to launch to use unity API without conflicts
#
# Author: Andrea Stagi (aka 4ndreaSt4gi)
# May 22, 2012

try:
    import dbus
    import atexit
    import dbus.service
    from signal import SIGTERM
    from dbus.mainloop.glib import DBusGMainLoop
    from gi.repository import Unity, GObject, Dbusmenu
    UNITY_SUPPORT = True
except Exception, e:
    print 'Could not load all modules for Unity support: %s' % e
    UNITY_SUPPORT = False

import os

BUS_NAME = "org.turpial.ve"
CONTROLLER_OBJ_PATH = "/org/turpial/ve/turpialunity"

class Daemon:
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self.pidfile,'w+').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        pass

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
    def add_quicklist_button(self, label, visible):

        def _pressCallback(arg1, arg2, arg3):
            self.buttonPressed(label)

        item = Dbusmenu.Menuitem.new()
        item.property_set(Dbusmenu.MENUITEM_PROP_LABEL, label)
        item.property_set_bool(Dbusmenu.MENUITEM_PROP_VISIBLE, visible)
        item.connect("item-activated", _pressCallback, None)
        self.ql.child_append(item)
        self.launcher.set_property("quicklist", self.ql)

    @dbus.service.method(BUS_NAME)
    def add_quicklist_checkbox(self, label, visible, status):

        def _check_callback(menuitem, a, b):
            if menuitem.property_get_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE) == Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED:
                menuitem.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_UNCHECKED)
                self.checkChanged(label, False)
            else:
                menuitem.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED)
                self.checkChanged(label, True)

        check = Dbusmenu.Menuitem.new ()
        check.property_set (Dbusmenu.MENUITEM_PROP_LABEL, label)
        check.property_set (Dbusmenu.MENUITEM_PROP_TOGGLE_TYPE, Dbusmenu.MENUITEM_TOGGLE_CHECK)
        check.property_set_int (Dbusmenu.MENUITEM_PROP_TOGGLE_STATE, Dbusmenu.MENUITEM_TOGGLE_STATE_CHECKED)
        check.property_set_bool (Dbusmenu.MENUITEM_PROP_VISIBLE, visible)
        check.connect (Dbusmenu.MENUITEM_SIGNAL_ITEM_ACTIVATED, _check_callback, None)
        self.ql.child_append(check)
        self.launcher.set_property("quicklist", self.ql)


    @dbus.service.method(BUS_NAME)
    def quit(self):
        self.loop.quit()

    @dbus.service.signal(BUS_NAME)
    def buttonPressed(self, signal):
        pass

    def checkChanged(self, signal, value):
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

def main():
    if len(sys.argv) != 2:
        print "Usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

    try:
        daemon = TurpialUnityDaemon('/tmp/turpial-unity-daemon.pid')
    except Exception, e:
        print "Error running the Unity Daemon: %s" % e
        sys.exit(-1)

    cmd = sys.argv[1]
    if cmd == 'start':
        daemon.start()
    elif cmd == 'stop':
        daemon.stop()
    elif cmd == 'restart':
        daemon.restart()
    else:
        print "Unknown command"
        sys.exit(2)

if __name__ == '__main__':
    main()

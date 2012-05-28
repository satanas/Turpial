UNITY_SUPPORT = False
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


# -*- coding: utf-8 -*-

# Utilities for Turpial interfaces
#
# Author: Wil Alvarez (aka Satanas)
# Oct 07, 2011

from libturpial.common.tools import *

try:
    # TODO: Implement this function for other platforms
    if detect_os() == OS_LINUX:
        import ctypes
        libc = ctypes.CDLL('libc.so.6')
        libc.prctl(15, 'turpial', 0, 0)
except ImportError:
    pass

INTERFACES = {}
DEFAULT_INTERFACE = None
CMD_VERSION = None
GTK_VERSION = None
QT_VERSION = None

# Load cmd
try:
    from turpial.ui.cmd.main import Main as _CMD
    from turpial.ui.cmd.main import VERSION as _CMDVERSION
    INTERFACES['cmd'] = _CMD
    DEFAULT_INTERFACE = 'cmd'
    CMD_VERSION = _CMDVERSION
except ImportError, exc:
    print exc

# Load gtk
try:
    from turpial.ui.gtk.main import Main as _GTK
    INTERFACES['gtk'] = _GTK
    DEFAULT_INTERFACE = 'gtk'
except ImportError, exc:
    print exc

# Load qt
try:
    from turpial.ui.qt.main import Main as _QT
    INTERFACES['qt'] = _QT
    DEFAULT_INTERFACE = 'qt'
except ImportError, exc:
    print exc

def available_interfaces():
    ui_availables = ''
    for ui in INTERFACES.keys():
        ui_availables += ui + '-'
    ui_availables = ui_availables[:-1] + ''
    return ui_availables

def default_interface():
    return INTERFACES[0]

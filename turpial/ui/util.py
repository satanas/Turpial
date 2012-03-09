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
except ImportError, exc:
    print exc

INTERFACES = {}
DEFAULT_INTERFACE = None

# Load cmd
try:
    from turpial.ui.cmd.main import Main as _CMD
    INTERFACES['cmd'] = _CMD
    DEFAULT_INTERFACE = 'cmd'
except ImportError, exc:
    print 'Could not initialize CMD interface.'
    print exc

# Load gtk
try:
    from turpial.ui.gtk.main import Main as _GTK
    INTERFACES['gtk'] = _GTK
    DEFAULT_INTERFACE = 'gtk'
except ImportError, exc:
    print 'Could not initialize GTK interface.'
    print exc

# Load qt
try:
    from turpial.ui.qt.main import Main as _QT
    INTERFACES['qt'] = _QT
    DEFAULT_INTERFACE = 'qt'
except ImportError, exc:
    print 'Could not initialize QT interface.'
    print exc

def available_interfaces():
    return ', '.join(INTERFACES.keys())

def default_interface():
    return INTERFACES['gtk']


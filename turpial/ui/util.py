# -*- coding: utf-8 -*-

# Utilities for Turpial interfaces

import xml.sax.saxutils as saxutils

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

# Load gtk3
#try:
#    from turpial.ui.gtk.main import Main as _GTK
#    INTERFACES['gtk'] = _GTK
#    DEFAULT_INTERFACE = DEFAULT_INTERFACE or 'gtk'
#except ImportError, exc:
#    print 'Could not initialize GTK interface.'
#    print exc

# Load qt
try:
    from turpial.ui.qt.main import Main as _QT
    INTERFACES['qt'] = _QT
    DEFAULT_INTERFACE = DEFAULT_INTERFACE or 'qt'
except ImportError, exc:
    print 'Could not initialize QT interface.'
    print exc

# Load cmd
try:
    from turpial.ui.cmd.main import Main as _CMD
    INTERFACES['cmd'] = _CMD
    DEFAULT_INTERFACE = DEFAULT_INTERFACE or 'cmd'
except ImportError, exc:
    print 'Could not initialize CMD interface.'
    print exc

def available_interfaces():
    return ', '.join(INTERFACES.keys())

def unescape_text(text):
    text = saxutils.unescape(text)
    text = text.replace('&quot;', '"')
    text = text.replace('\r\n', ' ')
    text = text.replace('\n', ' ')
    return text


def humanize_size(self, size):
    if size == 0:
        return '0 B'

    kbsize = size / 1024
    if kbsize > 0:
        mbsize = kbsize / 1024
        if mbsize > 0:
            gbsize = mbsize / 1024
            if gbsize > 0:
                return "%.2f GB" % (mbsize / 1024.0)
            else:
                return "%.2f MB" % (kbsize / 1024.0)
        else:
            return "%.2f KB" % (size / 1024.0)
    else:
        return "%.2f B" % size

def humanize_timestamp(self, status_timestamp):
	now = time.time()
	# FIXME: Workaround to fix the timestamp
	offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
	seconds = now - status_timestamp + offset

	minutes = seconds / 60.0
	if minutes < 1.0:
		timestamp = i18n.get('now')
	else:
		if minutes < 60.0:
			timestamp = "%i m" % minutes
		else:
			hours = minutes / 60.0
			if hours < 24.0:
				timestamp = "%i h" % hours
			else:
				dt = time.localtime(status_timestamp)
				month = time.strftime(u'%b', dt)
				year = dt.tm_year

				if year == time.localtime(now).tm_year:
					timestamp = u"%i %s" % (dt.tm_mday, month)
				else:
					timestamp = u"%i %s %i" % (dt.tm_mday, month, year)
	return timestamp

def humanize_time_intervals(self, interval):
	if interval > 1:
		unit = i18n.get('minutes')
	else:
		unit = i18n.get('minute')
	return " ".join([str(interval), unit])

def get_shortcut_string(self, key):
	return "+".join([self.shortcut_key, key])


# -*- coding: utf-8 -*-

# Ventana para subir el ego de los desarrolladores de Turpial xD
#
# Author: Wil Alvarez (aka Satanas)
# Dic 21, 2009

import os

from gi.repository import Gtk

from turpial import NAME
from turpial import VERSION

class About:
    def __init__(self, parent=None):
        about = Gtk.AboutDialog()
        about.set_logo(parent.load_image('turpial.png', True))
        about.set_name(NAME)
        about.set_version(VERSION)
        about.set_copyright('Copyright (C) 2009 - 2012 Wil Alvarez')
        about.set_comments(_('Microblogging client written in Python'))
        about.set_website('http://turpial.org.ve')

        try:
            path = os.path.realpath(os.path.join(os.path.dirname(__file__), 
                '..', '..', '..', 'COPYING'))
            lic = file(path, 'r')
            license = lic.read()
            lic.close()
        except Exception, msg:
            license =  'This script is free software; you can redistribute it '
            license += 'and/or modify it under the\nterms of the GNU General Public '
            license += 'License as published by the Free Software\nFoundation; either ' 
            license += 'version 3 of the License, or (at your option) any later version.'
            license += '\n\nYou should have received a copy of the GNU General Public '
            license += 'License along with\nthis script (see license); if not, write to '
            license += 'the Free Software\nFoundation, Inc., 59 Temple Place, Suite 330, '
            license += 'Boston, MA  02111-1307  USA'
        about.set_license(license)
        authors = []
        try:
            path = os.path.realpath(os.path.join(os.path.dirname(__file__), 
                '..', '..', '..', 'AUTHORS'))
            f = file(path, 'r')
            for line in f:
                authors.append(line.strip('\n'))
            f.close()
        except Exception, msg:
            authors = [_("File 'AUTHORS' not found")]
        about.set_authors(authors)

        about.connect("response", self.__response)
        about.connect("close", self.__close)
        about.connect("delete_event", self.__close)

        about.show()

    def __response(self, dialog, response, *args):
        if response < 0:
            dialog.destroy()
            dialog.emit_stop_by_name('response')

    def __close(self, widget, event=None):
        widget.destroy()
        return True

# -*- coding: utf-8 -*-

# Ventana para subir el ego de los desarrolladores de Turpial xD
#
# Author: Wil Alvarez (aka Satanas)
# Dic 21, 2009

import os

from gi.repository import Gtk

from turpial import NAME
from turpial import VERSION
from turpial.ui.lang import i18n

class AboutDialog(Gtk.AboutDialog):
    def __init__(self, parent=None):
        Gtk.AboutDialog.__init__(self)
        self.set_logo(parent.load_image('turpial.png', True))
        self.set_name(NAME)
        self.set_version(VERSION)
        self.set_copyright('Copyright (C) 2009 - 2012 Wil Alvarez')
        self.set_comments(i18n.get('about_description'))
        self.set_website('http://turpial.org.ve')

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
        self.set_license(license)
        authors = []
        try:
            path = os.path.realpath(os.path.join(os.path.dirname(__file__), 
                '..', '..', '..', 'AUTHORS'))
            f = file(path, 'r')
            for line in f:
                authors.append(line.strip('\n'))
            f.close()
        except Exception, msg:
            authors = [i18n.get('file_not_found')]
        self.set_authors(authors)

        self.connect("response", self.__response)
        self.connect("close", self.__close)
        self.connect("delete_event", self.__close)


    def __response(self, dialog, response, *args):
        if response < 0:
            dialog.hide()
            dialog.emit_stop_by_name('response')

    def __close(self, widget, event=None):
        self.destroy()
        return True

    def quit(self):
        self.destroy()

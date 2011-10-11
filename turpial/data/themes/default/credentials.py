# -*- coding: utf-8 -*-

# Credentials dialog for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 11, 2011

import gtk

from turpial.ui.lang import i18n
from turpial.ui.gtk.dialogs.generic import GenericDialog

class CredentialsDialog(GenericDialog):
    def __init__(self, parent, message):
        GenericDialog.__init__(self, parent, i18n.get('credentials'), 
            message, 352, 162)
    
    def __ok(self, password, remember):
        print password, remember
        
    def __cancel(self):
        self.rtn = None
        self.quit_ = True
        
    def action_request(self, url):
        action = url.split(':')[0]
        try:
            args = url.split(':')[1].split('-%&%-')
        except IndexError:
            args = []
        if action == 'ok':
            self.__ok(args[0], args[1])
        elif action == 'cancel':
            self.__cancel()
    
    def link_request(self, url):
        pass
        
    def unclose(self, widget, event=None):
        self.__cancel()
        return False

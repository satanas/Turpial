# -*- coding: utf-8 -*-

# Vista en modo texto para Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2009

import getpass

class Main:
    def __init__(self, controller):
        self.controller = controller
        
    def main_loop(self):
        pass
    
    def show_main(self):
        pass
        
    def show_login(self):
        usuario = raw_input('Username: ')
        password = getpass.unix_getpass()
        self.controller.signup(usuario, password)


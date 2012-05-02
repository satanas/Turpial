# -*- coding: utf-8 -*-

# GTK account manager for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2011

from PyQt4 import QtGui
from PyQt4.QtWebKit import *
#import gtk
import logging
from PyQt4.QtCore import QUrl
from PyQt4.QtCore import QVariant
from PyQt4.QtCore import QThread 
from PyQt4.QtCore import QPropertyAnimation 

from turpial.ui.lang import i18n
from turpial.ui.html import HtmlParser
from turpial.ui.qt.htmlview import HtmlView
from turpial.ui.qt.htmlview import FireTrigger 

log = logging.getLogger('Qt-AccountsDialog')

class AccountsDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(AccountsDialog,self).__init__()
        self.moveToThread(QThread())
        
        self.mainwin = parent
        self.htmlparser = HtmlParser()
        self.setWindowTitle("Account Manager")
        self.resize(365,325)
        
        self.container = HtmlView()
        self.container.action_request.connect(self.__action_request)
        self.container.link_request.connect(self.__action_request)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container.view)
        self.setLayout(self.layout)

        self.showed = False
        self.showed = True 
        self.form = None
    
    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True

    def __action_request(self, url):
        action, args = self.htmlparser.parse_command(url)
        
        if action == "close":
            self.__close(widget)
        elif action == "new_account":
            self.setWindowTitle("Create Account")
            self.resize(290,200)
            page = self.htmlparser.account_form(self.mainwin.get_protocols_list())
            self.container.render(page)

        elif action == "save_account":
            self.mainwin.save_account(args[0], args[1], args[2])
            self.args = args

        elif action == "delete_account":
            self.mainwin.delete_account(args[0])
        elif action == "login":
            self.mainwin.single_login(args[0])

    def set_account_id(self,account_id):
        self.account_id = account_id


    def show_about_win(self):
            self.setWindowTitle("About")
            self.resize(400,270)

            page = self.htmlparser.about()
            self.container.view.setHtml(page)

    def show_auth_win(self,url):
            self.setWindowTitle("Auth Window")
            self.resize(800,600)

            self.layout.removeItem(self.layout.itemAt(0))
            self.container.view
            self.container = HtmlView()
            self.layout.addWidget(self.container.view)
            self.container.view.load(QUrl(url))
            self.container.load_finished.connect(self.read_code)

    def read_code(self):
        code = self.container.view.page().mainFrame().documentElement().findAll('code')
        if len(code) > 0:
            for each in code[0].attributeNames():
                print "attribute:",each

            self.resize(370,330)
            self.mainwin.__oauth_callback(code[0].toPlainText(),self.account_id)
            self.container.action_request.connect(self.__action_request)
            self.container.link_request.connect(self.__action_request)

    
    def update(self):
        if self.showed:
            self.resize(365,325)
            page = self.htmlparser.accounts(self.mainwin.get_all_accounts())
            self.container.view.setHtml(page)
    
    def cancel_login(self, message):
        if self.form:
            self.form.cancel(message)
            return True
        self.update()
        return False
    
    def done_login(self):
        if self.form:
            self.form.done()
            return True
        return False
    
    def show_now(self):
        if self.showed:
            pass
        else:
            self.showed = True
            self.update()
            self.show()
            self.resize(365,325)
    
    def quit(self):
        self.destroy()

class AccountForm(QtGui.QDialog):
    def __init__(self, mainwin, parent, user=None, pwd=None, protocol=None):
        super(AccountForm,self).__init__()
        
        self.mainwin = mainwin
        self.htmlparser = HtmlParser()
        self.setWindowTitle("Create Account")
        self.resize(290,200)
        
        self.container = HtmlView()

        self.container.action_request.connect(self.__action_request)
        self.container.link_request.connect(self.__action_request)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container.view)
        self.setLayout(self.layout)
        
        page = self.htmlparser.account_form(self.mainwin.get_protocols_list())
        self.container.render(page)
        self.show()
        self.working = False
        
    def __close(self, widget, event=None):
        if not self.working:
            self.destroy()
            return False
        else:
            return True
    
    def __action_request(self, url):
        action, args = self.htmlparser.parse_command(url)
        
        if action == "close":
            self.__close(widget)
        elif action == "save_account":
            self.working = True
            self.authwin = AuthForm(self.mainwin,self)
            self.authwin.show()
    
    def cancel(self, message):
        self.working = False
        self.container.execute("cancel_login('" + message + "');")
    
    def set_loading_message(self, message):
        pass
        
    def done(self):
        self.working = False
        self.destroy()



class AuthForm(QtGui.QDialog):
    def __init__(self, mainwin, parent, user=None, pwd=None, protocol=None):
        super(AuthForm,self).__init__()
        
        self.mainwin = mainwin
        self.htmlparser = HtmlParser()
        self.setWindowTitle("Create Account")
        self.resize(490,200)
        
        self.container = HtmlView()

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container.view)
        self.setLayout(self.layout)
        
        self.container.view.load(QUrl("http://www.google.com"))
        self.show()
        
    def load(self,url):
        self.container.view.load(QUrl(url))

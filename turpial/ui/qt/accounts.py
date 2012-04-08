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
        #gtk.Window.__init__(self)
        self.moveToThread(QThread())
        
        self.mainwin = parent
        self.htmlparser = HtmlParser()
        #self.set_title(i18n.get('accounts'))
        self.setWindowTitle("Account Manager")
        self.resize(365,325)
        #self.set_size_request(360, 320)
        #self.set_resizable(False)
        #self.set_icon(self.mainwin.load_image('turpial.png', True))
        #self.set_transient_for(parent)
        #self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        #self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        #self.connect('delete-event', self.__close)
        
        self.container = HtmlView()
        #self.container.connect('action-request', self.__action_request)
        self.container.action_request.connect(self.__action_request)
        self.container.link_request.connect(self.__action_request)
        #self.container.process_request.connect(self.__action_request)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container.view)
        self.setLayout(self.layout)

        self.showed = False
        self.showed = True 
        self.form = None
#        self.show_now()
    
    def __close(self, widget, event=None):
        self.showed = False
        self.hide()
        return True

    def __action_request(self, url):
        print "accion!!"
        action, args = self.htmlparser.parse_command(url)
        print action
        print args 
        
        if action == "close":
            self.__close(widget)
        elif action == "new_account":
            #self.acc = AccountForm(self.mainwin,self)
            self.setWindowTitle("Create Account")
            self.resize(290,200)
            #self.container.view.load(QUrl("http://www.google.com/"))
            page = self.htmlparser.account_form(self.mainwin.get_protocols_list())
            self.container.render(page)

            #self.form = AccountForm(self.mainwin, self)
        elif action == "save_account":
            self.mainwin.save_account(args[0], args[1], args[2])
            print args 
            self.args = args

        elif action == "delete_account":
            self.mainwin.delete_account(args[0])
        elif action == "login":
            self.mainwin.single_login(args[0])


    def show_auth_win(self,url):
            print "entrando a save_account para abrir google de prueba" 
            self.setWindowTitle("Auth Window")
            self.resize(800,600)
            #self.authwin = AuthForm(self.mainwin,self)

            #self.layout.removeItem(self.layout.itemAt(1))

            print "itemAt:",dir(self.layout.itemAt(0))
            self.layout.removeItem(self.layout.itemAt(0))
            self.container.view
            self.container = HtmlView()
            print "self.layout",dir(self.layout)
            self.layout.addWidget(self.container.view)
            #self.__init__(self)
            print "index:",self.layout.indexOf(self.container.view)
            self.container.view.load(QUrl(url))
            self.container.load_finished.connect(self.read_code)
            #self.container.view.reload()
            #self.authwin.load("htt://www.google.com")
            #self.container.render("Hola")
            print "la listo segun eso"
            #self.authwin.show()


    def read_code(self):
        code = self.container.view.page().mainFrame().documentElement().findAll('code')
        print "len ",len(code)
        if len(code) > 0:
            for each in code[0].attributeNames():
                print "attribute:",each
            print "dir code: ",code[0].toPlainText()

            self.resize(365,325)
            self.mainwin.__oauth_callback(code[0].toPlainText(),self.mainwin.account_id)
            self.container.action_request.connect(self.__action_request)
            self.container.link_request.connect(self.__action_request)

    
    def update(self):
        if self.showed:
            self.resize(365,325)
            page = self.htmlparser.accounts(self.mainwin.get_all_accounts())
            #page = self.htmlparser.account_form(self.mainwin.get_protocols_list())
            #self.container.view.load(QUrl("http://www.google.com/"))
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
            print "showed"
            pass
            #self.present()
        else:
            print "showing"
            self.showed = True
            self.update()
            #self.show_all()
            self.show()
            self.resize(365,325)
    
    def quit(self):
        self.destroy()

class AccountForm(QtGui.QDialog):
    def __init__(self, mainwin, parent, user=None, pwd=None, protocol=None):
        super(AccountForm,self).__init__()
        #gtk.Window.__init__(self)
        
        self.mainwin = mainwin
        #self.set_transient_for(parent)
        #self.set_modal(True)
        self.htmlparser = HtmlParser()
        #self.set_title(i18n.get('create_account'))
        self.setWindowTitle("Create Account")
        self.resize(290,200)
        #self.set_size_request(290, 200)
        #self.set_resizable(False)
        #self.set_position(gtk.WIN_POS_CENTER)
        #self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        #self.connect('delete-event', self.__close)
        
        self.container = HtmlView()
        #self.container.connect('action-request', self.__action_request)

        self.container.action_request.connect(self.__action_request)
        self.container.link_request.connect(self.__action_request)

        #self.add(self.container)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container.view)
        self.setLayout(self.layout)
        
        page = self.htmlparser.account_form(self.mainwin.get_protocols_list())
        self.container.render(page)
        #self.container.view.load(QUrl("http://www.google.com/"))
        print "la listo segun eso2"
        self.show()
        self.working = False
        
    def __close(self, widget, event=None):
        if not self.working:
            self.destroy()
            return False
        else:
            return True
    
    def __action_request(self, url):
        print "accion!!!"
        action, args = self.htmlparser.parse_command(url)
        print "processing ",action
        
        if action == "close":
            self.__close(widget)
        elif action == "save_account":
            self.working = True
            print "entrando a save_account para abrir google de prueba" 
            self.authwin = AuthForm(self.mainwin,self)
            #self.container.view.load(QUrl("http://www.google.com/"))
            print "la listo segun eso"
            self.authwin.show()
            #self.mainwin.save_account(args[0], args[1], args[2])
    
    def cancel(self, message):
        self.working = False
        self.container.execute("cancel_login('" + message + "');")
    
    def set_loading_message(self, message):
        pass
        #self.container.execute("set_loading_message('" + message + "');")
        
    def done(self):
        self.working = False
        self.destroy()



class AuthForm(QtGui.QDialog):
    def __init__(self, mainwin, parent, user=None, pwd=None, protocol=None):
        super(AuthForm,self).__init__()
        #gtk.Window.__init__(self)
        
        self.mainwin = mainwin
        #self.set_transient_for(parent)
        #self.set_modal(True)
        self.htmlparser = HtmlParser()
        #self.set_title(i18n.get('create_account'))
        self.setWindowTitle("Create Account")
        self.resize(490,200)
        #self.set_size_request(290, 200)
        #self.set_resizable(False)
        #self.set_position(gtk.WIN_POS_CENTER)
        #self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        #self.connect('delete-event', self.__close)
        
        self.container = HtmlView()
        #self.container.connect('action-request', self.__action_request)

        #self.container.action_request.connect(self.__action_request)
        #self.container.link_request.connect(self.__action_request)

        #self.add(self.container)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container.view)
        self.setLayout(self.layout)
        
        #page = self.htmlparser.account_form(self.mainwin.get_protocols_list())
        #self.container.render(page)
        print "mandando a cargar google en autoform"
        self.container.view.load(QUrl("http://www.google.com"))
        self.show()
        print "listo"
        
    def load(self,url):
        print "poniendo a cargar",url
        self.container.view.load(QUrl(url))

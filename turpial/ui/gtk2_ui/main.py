# -*- coding: utf-8 -*-

# Vista Webkit para Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Feb 15, 2010

import gtk
import webkit
import gobject

from core.ui.base_ui import *
from core.ui.notification import *

gobject.threads_init()

class Main(BaseGui, gtk.Window):
    def __init__(self, controller):
        BaseGui.__init__(self, controller)
        gtk.Window.__init__(self)
        
        self.set_title('Turpial')
        self.set_size_request(280, 350)
        self.set_default_size(320, 480)
        self.current_width = 320
        self.current_height = 480
        self.set_icon(util.load_image('turpial_icon.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect('delete-event', self.__close)
        #self.connect('size-request', self.size_request)
        
        self.mode = 0
        self.vbox = None
        
        self.webview = webkit.WebView()
        self.settings = webkit.WebSettings()
        self.webview.set_settings(self.settings)
        
        scroll = gtk.ScrolledWindow()
        scroll.add(self.webview)
        
        # Valores de config. por defecto
        self.showed = True
        self.minimize = 'on'
        self.workspace = 'single'
        self.link_color = 'ff6633'
        self.home_interval = -1
        self.replies_interval = -1
        self.directs_interval = -1
        self.me = None
        self.version = None
        
        self.home_timer = None
        self.replies_timer = None
        self.directs_timer = None
        
        self.notify = Notification()
        
        #self.updatebox = UpdateBox(self)
        #self.replybox = ReplyBox(self)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(scroll, True, True, 2)
        self.add(self.vbox)
        self.show_all()
        
        self.webview.connect("navigation-requested", self.on_click_link)
        
        self.__create_trayicon()
        
    def on_click_link(self, view, frame, req):
        uri = req.get_uri()
        print uri
        if uri == 'internal': return False
        
        if uri == 'login':
            self.webview.load_string('hola', "text/html", "iso-8859-15", "internal")
            return True
        return False
        
    def __create_trayicon(self):
        if gtk.check_version(2, 10, 0) is not None:
            self.log.debug("Disabled Tray Icon. It needs PyGTK >= 2.10.0")
            return
        self.tray = gtk.StatusIcon()
        self.tray.set_from_pixbuf(util.load_image('turpial_icon.png', True))
        self.tray.set_tooltip('Turpial')
        self.tray.connect("activate", self.__on_trayicon_click)
        self.tray.connect("popup-menu", self.__show_tray_menu)
        
        
    def __on_trayicon_click(self, widget):
        if(self.showed is True):
            self.showed = False
            self.hide()
        else:
            self.showed = True
            self.show()
            #self.present()
            
    def __show_tray_menu(self, widget, button, activate_time):
        menu = gtk.Menu()
        tweet = gtk.MenuItem('Tweet')
        exit = gtk.MenuItem('Salir')
        if self.mode == 2:
            menu.append(tweet)
        menu.append(exit)
        
        exit.connect('activate', self.quit)
        tweet.connect('activate', self.__show_update_box_from_menu)
            
        menu.show_all()
        menu.popup(None, None, None, button, activate_time)
        
    def __show_update_box_from_menu(self, widget):
        self.show_update_box()
        
    def __close(self, widget, event=None):
        if self.minimize == 'on':
            self.showed = False
            self.hide()
        else:
            self.quit(widget)
        return True
    
    def quit(self, widget):
        #self.__save_size()
        gtk.main_quit()
        self.destroy()
        self.tray = None
        self.request_signout()
        
    def main_loop(self):
        gtk.gdk.threads_enter()
        gtk.main()
        gtk.gdk.threads_leave()
        
    def show_login(self):
        self.mode = 1
        temp = '''<html>
            <head></head>
            <title></title>
            <body>
                <p>Usuario y contrase&ntilde;a:</p>
                <form method="post" action="login">
                <input type="text" id="username" name="username" /><br/>
                <input type="text" id="password" name="password" /><br/>
                <input type="submit" value="Entrar"/><br/>
                </form>
            </body>
            </html>'''
        
        self.webview.load_string(temp, "text/html", "iso-8859-15", "internal")

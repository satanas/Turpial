# -*- coding: utf-8 -*-

# GTK main view for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Sep 03, 2011

import os
import gtk
import sys
import Queue
import logging
import threading

from turpial.ui.lang import i18n
from turpial.ui.base import Base
from turpial.ui.html import HtmlParser
from turpial.ui.gtk.about import About
from turpial.ui.gtk.htmlview import HtmlView
from turpial.ui.gtk.accounts import Accounts
from turpial.ui.gtk.dialogs.credentials import CredentialsDialog

from libturpial.common import ColumnType

gtk.gdk.set_program_class("Turpial")
gtk.gdk.threads_init()

log = logging.getLogger('Gtk')

class Main(Base, gtk.Window):
    def __init__(self, core):
        Base.__init__(self, core)
        gtk.Window.__init__(self)
        
        self.htmlparser = HtmlParser(core.list_protocols())
        self.set_title('Turpial')
        self.set_size_request(280, 350)
        self.set_default_size(352, 482)
        self.set_icon(self.load_image('turpial.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        self.connect('key-press-event', self.__on_key_press)
        self.connect('focus-in-event', self.__on_focus)
        
        self.container = HtmlView()
        self.container.connect('action-request', self.__action_request)
        self.container.connect('link-request', self.__link_request)
        self.add(self.container)
        
        self.mode = 0
        
        # Configuration
        self.showed = True
        self.minimize = 'on'
        self.version = '2.x'
        
        self.timer1 = None
        self.timer2 = None
        self.timer3 = None
        self.interval1 = -1
        self.interval2 = -1
        self.interval3 = -1
        
        '''
        self.win_state = 'windowed'
        self.workspace = 'single'
        self.link_color = '#ff6633'
        '''
        
        #self.sound = Sound()
        #self.notify = Notification(controller.no_notif)
        self.accounts = Accounts(self)
        
        #self.worker2 = Worker2()
        #self.worker2.start()
        self.worker = Worker()
        self.worker.start()
        
        self.__create_trayicon()
        self.show_all()
        
    def __action_request(self, widget, url):
        action = url.split(':')[0]
        try:
            args = url.split(':')[1].split('-%&%-')
        except IndexError:
            args = []
        print url
        #print action, args
        
        if action == 'about':
            self.show_about()
        elif action == 'settings':
            self.container.execute("alert('hola');")
        elif action == 'accounts':
            self.accounts.show(self.core.all_accounts())
        elif action == 'save_account':
            pass
        elif action == 'delete_account':
            pass
        elif action == 'login':
            acc_login = []
            for acc in self.core.all_accounts():
                if acc.id_ in args:
                    acc.activate(True)
                    if not acc.is_remembered():
                        gtk.gdk.threads_enter()
                        dialog = CredentialsDialog(self, acc.id_)
                        response = dialog.run()
                        passwd = dialog.password.get_text()
                        rem = dialog.remember.get_active()
                        dialog.destroy()
                        gtk.gdk.threads_leave()
                        if response == gtk.RESPONSE_ACCEPT:
                            acc.update(passwd, rem)
                            acc_login.append(acc)
                    else:
                        acc_login.append(acc)
                else:
                    acc.activate(False)
            
            # If there is no accounts then cancel_login
            if len(acc_login) == 0:
                msg = i18n.get('login_cancelled')
                self.container.execute("cancel_login('" + msg + "');")
                return
            
            # show main
            for acc in acc_login:
                #self.core.login(acc.id_)
                self.worker.register(self.core.login, (acc.id_), self.__test)
    
    def __test(self, arg):
        print 'resp', arg, arg.code, arg.errmsg, arg.items
        
        if arg.code > 0:
            #msg = i18n.get(rtn.errmsg)
            msg = arg.errmsg
            self.container.execute("cancel_login('" + msg + "');")
            return
        
        auth_obj = arg.items
        if auth_obj.must_auth():
            print "Please visit %s, authorize Turpial and type the pin returned" % auth_obj.url
            #pin = self.__user_input('Pin: ')
            #self.core.authorize_oauth_token(acc, pin)
        
        self.worker.register(self.core.auth, (auth_obj.account), self.__test2)        
            
    def __test2(self, arg):
        if arg.code > 0:
            msg = arg.errmsg
            self.container.execute("cancel_login('" + msg + "');")
            return
        else:
            print 'Logged in with account %s' % arg.items.id_.split('-')[0]
    
    def __link_request(self, widget, url):
        print 'requested link: %s' % url
        
    def __create_trayicon(self):
        if gtk.check_version(2, 10, 0) is not None:
            log.debug("Disabled Tray Icon. It needs PyGTK >= 2.10.0")
            return
        self.tray = gtk.StatusIcon()
        self.tray.set_from_pixbuf(self.load_image('turpial-tray.png', True))
        self.tray.set_tooltip('Turpial')
        self.tray.connect("activate", self.__on_trayicon_click)
        self.tray.connect("popup-menu", self.__show_tray_menu)
        
    def __on_trayicon_click(self, widget):
        if self.showed:
            self.showed = False
            self.hide()
        else:
            self.showed = True
            self.show()
            
    def __on_focus(self, widget, event):
        self.tray.set_from_pixbuf(self.load_image('turpial-tray.png', True))
    
    def __on_key_press(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if (event.state & gtk.gdk.CONTROL_MASK) and keyname.lower() == 'n':
            self.show_update_box()
            return True
        return False
        
    def __show_tray_menu(self, widget, button, activate_time):
        menu = gtk.Menu()
        tweet = gtk.MenuItem(i18n.get('tweet'))
        follow = gtk.MenuItem(i18n.get('follow'))
        exit_ = gtk.MenuItem(i18n.get('exit'))
        if self.mode == 2:
            menu.append(tweet)
            menu.append(follow)
            menu.append(gtk.SeparatorMenuItem())
        menu.append(exit_)
        
        exit_.connect('activate', self.main_quit)
        #tweet.connect('activate', self.__show_update_box_from_menu)
        #follow.connect('activate', self.__show_follow_box_from_menu)
        
        menu.show_all()
        menu.popup(None, None, None, button, activate_time)
        
    def __close(self, widget, event=None):
        if self.minimize == 'on':
            self.showed = False
            self.hide()
        else:
            self.main_quit()
        return True
        
    def main_quit(self, widget=None):
        self.log.debug('Exit')
        self.destroy()
        self.tray = None
        self.worker.quit()
        self.worker.join()
        if widget:
            gtk.main_quit()
        sys.exit(0)
        
    def main_loop(self):
        try:
            gtk.gdk.threads_enter()
            gtk.main()
            gtk.gdk.threads_leave()
        except Exception:
            sys.exit(0)
    
    def show_login(self):
        page = self.htmlparser.main([], []) #['satanas82-twitter-timeline', 'satanas-identica-timeline'])
        self.container.render(page)
        
    def show_about(self):
        about = About(self)
        
    def load_image(self, path, pixbuf=False):
        img_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', '..', 'data', 'pixmaps', path))
        pix = gtk.gdk.pixbuf_new_from_file(img_path)
        if pixbuf: return pix
        avatar = gtk.Image()
        avatar.set_from_pixbuf(pix)
        del pix
        return avatar
        
class Worker2:
    def __init__(self):
        self.queue = Queue.Queue()
        self.exit_ = False
    
    def register(self, funct, args, callback):
        self.queue.put((funct, args, callback))
    
    def login(self, acc_id, callback):
        self.__register(self.protocol.auth, (acc_id), callback)
    
    def quit(self):
        self.exit_ = True
    
    def start(self):
        while not self.exit_:
            try:
                req = self.queue.get(True, 0.3)
            except Queue.Empty:
                continue
            except:
                continue
            
            (funct, args, callback) = req
            
            
            thread = Thread(rtn=funct, args=args)
            thread.start()
            thread.join()
            
            if callback:
                callback(rtn)
    
        

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.queue = Queue.Queue()
        self.exit_ = False 
    
    def register(self, funct, args, callback):
        self.queue.put((funct, args, callback))
    
    def quit(self):
        self.exit_ = True
        
    def run(self):
        while not self.exit_:
            try:
                req = self.queue.get(True, 0.3)
            except Queue.Empty:
                continue
            except:
                continue
            
            (funct, args, callback) = req
            print funct, args, callback
            
            rtn = funct(args)
            if callback:
                callback(rtn)


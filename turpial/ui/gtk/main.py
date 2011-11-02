# -*- coding: utf-8 -*-

# GTK main view for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Sep 03, 2011

import os
import gtk
import sys
import gobject
import logging

from libturpial.common import ColumnType

from turpial.ui.lang import i18n
from turpial.ui.base import Base
from turpial.ui.html import HtmlParser
from turpial.ui.gtk.about import About
from turpial.ui.gtk.worker import Worker
from turpial.ui.gtk.htmlview import HtmlView
from turpial.ui.gtk.accounts import Accounts

gtk.gdk.set_program_class("Turpial")
gtk.gdk.threads_init()

log = logging.getLogger('Gtk')

class Main(Base, gtk.Window):
    def __init__(self, core, config):
        Base.__init__(self, core, config)
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
        
        self.columns = []
        self.updating = []
        
        '''
        self.win_state = 'windowed'
        self.workspace = 'single'
        self.link_color = '#ff6633'
        '''
        
        #self.sound = Sound()
        #self.notify = Notification(controller.no_notif)
        
        #self.worker2 = Worker2()
        #self.worker2.start()
        self.worker = Worker()
        self.worker.set_timeout_callback(self.__timeout_callback)
        self.worker.start()
        
        # Persistent dialogs
        self.accounts = Accounts(self)
        
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
        
        if action == '//about':
            self.show_about()
        elif action == '//settings':
            self.container.execute("alert('hola');")
        elif action == '//accounts':
            self.accounts.show()
            
    def __link_request(self, widget, url):
        self.open_url(url)
        
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
    
    def __timeout_callback(self, funct, arg):
        gobject.timeout_add(200, funct, arg)
        
    def __login_callback(self, arg):
        if arg.code > 0:
            #msg = i18n.get(rtn.errmsg)
            msg = arg.errmsg
            print msg
            return
        
        auth_obj = arg.items
        if not auth_obj.must_auth():
            self.auth(auth_obj.account)
    
    def __done_callback(self, arg):
        if arg.code > 0:
            msg = arg.errmsg
            print msg
        
        self.download_stream1()
    
    def __update_column_streams(self):
        self.columns = []
        self.updating = []
        for i in range(1,4):
            name = "column%i" % i
            col = self.config.read('Columns', name)
            if col != '':
                self.columns.append(col)
                self.updating.append(False)
    
    def load_image(self, path, pixbuf=False):
        img_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', '..', 'data', 'pixmaps', path))
        pix = gtk.gdk.pixbuf_new_from_file(img_path)
        if pixbuf: return pix
        avatar = gtk.Image()
        avatar.set_from_pixbuf(pix)
        del pix
        return avatar
    
    def main_quit(self, widget=None):
        self.log.debug('Exit')
        self.destroy()
        self.tray = None
        self.accounts.quit()
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
    
    def show_main(self):
        self.__update_column_streams()
        page = self.htmlparser.main(self.core.list_accounts(), self.columns)
        self.container.render(page)
        self.login()
        
    def show_about(self):
        about = About(self)
    
    def login(self):
        for acc in self.core.list_accounts():
            self.worker.register(self.core.login, (acc), self.__login_callback)
    
    def auth(self, acc):
        self.worker.register(self.core.auth, (acc), self.__done_callback)
    
    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------
    
    def download_stream1(self):
        try:
            test = self.columns[0]
        except IndexError:
            return True
        
        if self.updating[0]: return True
        
        self.updating[0] = True
        temp = self.columns[0].rfind('-')
        acc_id = self.columns[0][:temp]
        col_id = self.columns[0][temp + 1:]
        self.worker.register(self.core.get_column_statuses, (acc_id, col_id), self.update_column1)
        return True
        
    def download_rates(self):
        self.__controller._update_rate_limits()
        return True
        
    def download_favorites(self):
        self.__controller._update_favorites()
        return True
        
    def download_friends(self):
        self.__controller._update_friends()
        return True
        

    def start_updating_column1(self):
        self.home.timeline.start_update()
        
    def start_updating_column2(self):
        self.home.replies.start_update()
        
    def start_updating_column3(self):
        self.home.direct.start_update()
        
    def start_search(self):
        self.profile.search.start_update()
        
    def update_column1(self, arg):
        if arg.code > 0:
            print arg.errmsg
            return
        
        page = self.htmlparser.render_statuses(arg.items)
        self.container.update_element("list1", page)
        '''
        gtk.gdk.threads_enter()
        
        last = self.home.timeline.statuslist.last
        count = self.home.timeline.update_tweets(tweets)
        column = self.request_viewed_columns()[0]
        show_notif = self.read_config_value('Notifications', 'home')
        
        log.debug(u'Actualizando %s' % column.title)
        if self.updating[0] and show_notif == 'on':
            self._notify_new_tweets(column, tweets, last, count)
            
        gtk.gdk.threads_leave()
        '''
        self.updating[0] = False

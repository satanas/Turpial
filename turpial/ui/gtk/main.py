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
from turpial.ui.gtk.accounts import AccountsDialog
from turpial.ui.gtk.oauthwin import OAuthWindow

gtk.gdk.set_program_class("Turpial")
gtk.gdk.threads_init()

log = logging.getLogger('Gtk')

class Main(Base, gtk.Window):
    def __init__(self, core, config):
        Base.__init__(self, core, config)
        gtk.Window.__init__(self)
        
        self.htmlparser = HtmlParser()
        self.set_title('Turpial')
        self.set_size_request(310, 350)
        self.set_default_size(310, 482)
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
        self.curr_acc = None
        
        # Configuration
        self.showed = True
        self.minimize = 'on'
        
        self.timers = {}
        self.interval1 = -1
        self.interval2 = -1
        self.interval3 = -1
        
        self.updating = []
        
        #self.sound = Sound()
        #self.notify = Notification(controller.no_notif)
        
        self.worker = Worker()
        self.worker.set_timeout_callback(self.__timeout_callback)
        self.worker.start()
        
        # Persistent dialogs
        self.accountsdlg = AccountsDialog(self)
        
        self.__create_trayicon()
        self.show_all()
        
    def __action_request(self, widget, url):
        '''
        action = url.split(':')[0]
        try:
            args = url.split(':')[1].split(ARG_SEP)
        except IndexError:
            args = []
        '''
        action, args = self.htmlparser.parse_command(url)
        print url
        if action == 'about':
            self.show_about()
        elif action == 'settings':
            self.container.execute("alert('hola');")
        elif action == 'accounts_manager':
            self.accountsdlg.show()
        elif action == 'follow':
            pass
        elif action == 'add_column':
            self.__show_add_column_menu(widget)
        elif action == 'delete_column':
            self.delete_column(args[0])
            
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
    
    def __show_add_column_menu(self, widget):
        menu = gtk.Menu()
        
        public_tl = gtk.MenuItem(i18n.get('public_timeline'))
        public_tl_menu = gtk.Menu()
        public_tl_menu.append(gtk.MenuItem(i18n.get('twitter')))
        public_tl_menu.append(gtk.MenuItem(i18n.get('identica')))
        public_tl.set_submenu(public_tl_menu)
        
        search = gtk.MenuItem(i18n.get('search'))
        search_menu = gtk.Menu()
        search_menu.append(gtk.MenuItem(i18n.get('twitter')))
        search_menu.append(gtk.MenuItem(i18n.get('identica')))
        search.set_submenu(search_menu)
        
        empty = True
        accounts = self.get_all_accounts()
        columns = self.get_all_columns()
        
        for acc in accounts:
            name = "%s (%s)" % (acc.username, i18n.get(acc.protocol_id))
            temp = gtk.MenuItem(name)
            if acc.logged_in:
                temp_menu = gtk.Menu()
                for key, col in columns[acc.id_].iteritems():
                    item = gtk.MenuItem(key)
                    if col.id_ != "":
                        item.set_sensitive(False)
                    item.connect('activate', self.__add_column, col.build_id())
                    temp_menu.append(item)
                temp.set_submenu(temp_menu)
            else:
                temp.set_sensitive(False)
            menu.append(temp)
            empty = False
        
        if not empty:
            menu.append(gtk.SeparatorMenuItem())
        menu.append(public_tl)
        menu.append(search)
        menu.show_all()
        menu.popup(None, None, None, 0, gtk.get_current_event_time())
    
    def __add_column(self, widget, column_id):
        self.save_column(column_id)
        
    def __close(self, widget, event=None):
        if self.minimize == 'on':
            self.showed = False
            self.hide()
        else:
            self.main_quit()
        return True
    
    def __timeout_callback(self, funct, arg, user_data):
        if user_data:
            gobject.timeout_add(200, funct, arg, user_data)
        else:
            gobject.timeout_add(200, funct, arg)
    
    def __login_callback(self, arg):
        if arg.code > 0:
            #msg = i18n.get(rtn.errmsg)
            msg = arg.errmsg
            self.accountsdlg.cancel_login(msg)
            return
        
        auth_obj = arg.items
        if auth_obj.must_auth():
            oauthwin = OAuthWindow(self, self.accountsdlg.form)
            oauthwin.connect('response', self.__oauth_callback)
            oauthwin.connect('cancel', self.__cancel_callback)
            oauthwin.open(auth_obj.url)
        else:
            self.__auth_callback(arg)
    
    def __oauth_callback(self, widget, verifier):
        #self.form.set_loading_message(i18n.get('authorizing'))
        self.worker.register(self.core.authorize_oauth_token, (self.curr_acc, verifier), self.__auth_callback)
    
    def __cancel_callback(self, widget, reason):
        self.delete_account(self.curr_acc)
        self.accountsdlg.cancel_login(i18n.get(reason))
        self.curr_acc = None
    
    def __auth_callback(self, arg):
        if arg.code > 0:
            msg = arg.errmsg
            self.accountsdlg.cancel_login(msg)
        else:
            #self.form.set_loading_message(i18n.get('authenticating'))
            self.worker.register(self.core.auth, (self.curr_acc), self.__done_callback)
    
    def __done_callback(self, arg):
        if arg.code > 0:
            msg = arg.errmsg
            self.accountsdlg.cancel_login(msg)
            self.show_notice(msg, 'error')
        else:
            self.accountsdlg.done_login()
            self.accountsdlg.update()
        
            for col in self.get_registered_columns():
                if col.account_id == self.curr_acc:
                    self.download_stream(col)
                    self.__add_timer(col)
        
        self.curr_acc = None
    
    def show_notice(self, msg, type_):
        cmd = 'show_notice("%s", "%s");' % (msg, type_)
        self.container.execute(cmd)
        
    def __add_timer(self, column):
        #if (self.timer1 != home_interval):
        if self.timers.has_key(column.id_):
            gobject.source_remove(self.timers[column.id_])
        self.interval1 = 5
        self.timers[column.id_] = gobject.timeout_add(self.interval1 * 60 * 1000, 
            self.download_stream, column)
        log.debug('--Created timer for %s every %i min' % (column.id_, self.interval1))
    
    def __remove_timer(self, column_id):
        if self.timers.has_key(column_id):
            gobject.source_remove(self.timers[column_id])
            log.debug('--Removed timer for %s' % column_id)
            
    def get_protocols_list(self):
        return self.core.list_protocols()
    
    def get_all_accounts(self):
        return self.core.all_accounts()
    
    def get_accounts_list(self):
        return self.core.list_accounts()
        
    def get_all_columns(self):
        return self.core.all_columns()
    
    def get_registered_columns(self):
        return self.core.all_registered_columns()
    
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
        reg_columns = self.get_registered_columns()
        if len(reg_columns) == 0:
            page = self.htmlparser.empty()
        else:
            page = self.htmlparser.main(self.get_accounts_list(), reg_columns)
        self.container.render(page)
        self.login()
        
    def show_about(self):
        about = About(self)
    
    def login(self):
        for acc in self.get_accounts_list():
            self.curr_acc = acc
            self.worker.register(self.core.login, (acc), self.__login_callback)
                    
    def delete_account(self, account_id):
        self.core.unregister_account(account_id, True)
        self.accountsdlg.update()
    
    def save_account(self, username, protocol_id, password):
        self.curr_acc = self.core.register_account(username, protocol_id, password, True)
        self.worker.register(self.core.login, (self.curr_acc), self.__login_callback)
    
    def save_column(self, column_id):
        column = self.core.register_column(column_id)
        reg_columns = self.get_registered_columns()
        if len(reg_columns) == 1:
            page = self.htmlparser.main(self.get_accounts_list(), reg_columns)
            self.container.render(page)
        else:
            content = self.htmlparser.render_column(column)
            self.container.append_element('#content', content, 'add_column();')
        self.download_stream(column)
        self.__add_timer(column)
    
    def delete_column(self, column_id):
        self.core.unregister_column(column_id)
        reg_columns = self.get_registered_columns()
        if len(reg_columns) == 0:
            page = self.htmlparser.empty()
            self.container.render(page)
        else:
            self.container.execute('remove_column("' + column_id + '");')
        self.__remove_timer(column_id)
    
    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------
    
    def download_stream(self, column):
        '''
        print self.columns, self.columns[0]
        if not self.columns[0]: return True
        if self.columns[0].updating: return True
        self.columns[0].updating = True
        
        self.start_updating_column1()
        self.worker.register(self.core.get_column_statuses, (self.columns[0].account_id, 
            self.columns[0].column_id), self.update_column1)
        '''
        self.worker.register(self.core.get_column_statuses, (column.account_id, 
            column.column_name), self.update_column, column.id_)
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
        print 'Updating column 1'
        
    def start_updating_column2(self):
        self.home.replies.start_update()
        
    def start_updating_column3(self):
        self.home.direct.start_update()
        
    def start_search(self):
        self.profile.search.start_update()
        
    def update_column(self, arg, column_id):
        if arg.code > 0:
            print arg.errmsg
            return
        page = self.htmlparser.render_statuses(arg.items)
        element = "#list-%s" % column_id
        self.container.update_element(element, page, 'recalculate_column_size();')
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
        self.columns[0].updating = False
        '''
        

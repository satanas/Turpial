# -*- coding: utf-8 -*-

# Qt main view for Turpial

import os
import sys

# PyQt4 Support:
from PyQt4 import QtCore
from PyQt4.QtGui import QMenu
from PyQt4.QtGui import QImage
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QFontDatabase
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QApplication
#from PyQt4.QtWebKit import *
from PyQt4.QtCore import pyqtSignal

from turpial import DESC
from turpial.ui.base import *

from turpial.ui.qt.dock import Dock
from turpial.ui.qt.worker import Worker
from turpial.ui.qt.tray import TrayIcon
from turpial.ui.qt.update import UpdateBox
from turpial.ui.qt.oauth import OAuthDialog
from turpial.ui.qt.search import SearchDialog
from turpial.ui.qt.container import Container
from turpial.ui.qt.profile import ProfileDialog
from turpial.ui.qt.accounts import AccountsDialog
from turpial.ui.qt.selectfriend import SelectFriendDialog

from libturpial.api.core import Core
from libturpial.api.models.column import Column
from libturpial.common.tools import get_account_id_from, get_column_slug_from

class Main(Base, QWidget):

    #emitter = pyqtSignal(list)
    account_deleted = pyqtSignal()

    def __init__(self, core):
        self.app = QApplication(sys.argv)

        Base.__init__(self, core)
        QWidget.__init__(self)
        QFontDatabase.addApplicationFont('/home/satanas/proyectos/turpial2/turpial/data/fonts/RopaSans-Regular.ttf')
        QFontDatabase.addApplicationFont('/home/satanas/proyectos/turpial2/turpial/data/fonts/Monda-Regular.ttf')
        path = os.path.join(os.path.dirname(__file__), '../../data/fonts/Cicle_Gordita.ttf')
        id_ = QFontDatabase.addApplicationFont(path)
        path = os.path.join(os.path.dirname(__file__), '../../data/fonts/Aaargh.ttf.ttf')
        id_ = QFontDatabase.addApplicationFont(path)
        #QFontDatabase.addApplicationFont('/home/satanas/proyectos/turpial2/turpial/data/fonts/RopaSans-Regular.ttf')
        #QFontDatabase.addApplicationFont('/home/satanas/proyectos/turpial2/turpial/data/fonts/Monda-Regular.ttf')

        self.setWindowTitle('Turpial')
        self.ignore_quit = True
        self.resize(320, 480)
        self.showed = True

        self.tray = TrayIcon(self)
        self.tray.activated.connect(self.__on_tray_click)

        self.core = Core()

        self.worker = Worker()
        self.worker.start()

        #self.worker.register(self.core.list_accounts, None, self.__test)

        self._container = Container(self)
        self._container.empty()

        self.dock = Dock(self)
        self.dock.empty()

        self.dock.accounts_clicked.connect(self.show_accounts_dialog)
        self.dock.columns_clicked.connect(self.show_column_menu)

        #oauth_dialog = OAuthDialog(self, 'http://twitter.com')
        #self.profile = ProfileDialog(self)
        #self.profile.show()
        #search = SearchDialog(self)
        #friend = SelectFriendDialog(self)
        #self.update_box = UpdateBox(self)
        #self.update_box.show()

        #if len(self.base.get_accounts_list()) > 0:
        #    no_accounts.set_markup(i18n.get('no_registered_columns'))
        #else:
        #    no_accounts.set_markup(i18n.get('no_active_accounts'))

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self._container, 1)
        layout.addWidget(self.dock)
        layout.setMargin(0);

        self.setLayout(layout)


    def get_registered_columns(self):
        i = 1
        columns = []
        while True:
            column_num = "column%s" % i
            column_id = self.core.config.read('Columns', column_num)
            if column_id:
                account_id = get_account_id_from(column_id)
                column_slug = get_column_slug_from(column_id)
                columns.append(Column(account_id, column_slug))
                i += 1
            else:
                break
        return columns

    def __test(self, value):
        print value

    def start(self):
        print 'hola'


    #================================================================
    # Tray icon
    #================================================================

    def __on_tray_click(self):
        if self.showed:
            self.showed = False
            self.hide()
        else:
            self.showed = True
            self.show()

    #================================================================
    # Overrided methods
    #================================================================

    def main_loop(self):
        try:
            self.app.exec_()
        except Exception:
            sys.exit(0)

    def main_quit(self, widget=None, force=False):
        self.app.quit()
        sys.exit(0)

    def show_main(self):
        self.start()
        self.show()
        self.update_container()

    def load_image(self, filename, pixbuf=False):
        img_path = os.path.join(self.images_path, filename)
        if pixbuf:
            return QPixmap(img_path)
        return QImage(img_path)

    def get_image_path(self, filename):
        return os.path.join(self.images_path, filename)

    def update_container(self):
        accounts = self.get_registered_accounts()
        columns = self.get_registered_columns()
        if len(columns) == 0:
            if len(accounts) == 0:
                self._container.empty(False)
            else:
                self._container.empty(True)
            self.dock.empty()
            self.tray.empty()
        else:
            self._container.normal(columns)
            self.dock.normal()
            self.tray.normal()
            self.download_stream(columns[0])



    def show_accounts_dialog(self):
        accounts = AccountsDialog(self)

    def show_column_menu(self):
        empty = True
        columns = self.get_all_columns()
        reg_columns = self.get_registered_columns()
        accounts = self.get_all_accounts()

        self.columns_menu = QMenu(self)

        #if len(accounts) == 0:
        if True:
            empty_menu = QAction(i18n.get('no_registered_accounts'), self)
            empty_menu.setEnabled(False)
            self.columns_menu.addAction(empty_menu)
            self.columns_menu.exec_()
            return

        #for acc in :
        #    name = "%s (%s)" % (acc.username, i18n.get(acc.protocol_id))
        #    temp = QAction(name)

        #    # Build submenu for columns in each account
        #    temp_menu = Gtk.Menu()
        #    for key, col in columns[acc.id_].iteritems():
        #        item = Gtk.MenuItem(key)
        #        if col.id_ != "":
        #            item.set_sensitive(False)
        #        item.connect('activate', self.__save_column, col.build_id())
        #        temp_menu.append(item)
        #    # Add public timeline
        #    public_tl = Gtk.MenuItem(i18n.get('public_timeline').lower())
        #    public_tl.connect('activate', self.__save_column, acc.id_ + '-public')
        #    temp_menu.append(public_tl)

        #    temp.set_submenu(temp_menu)

        #    # Add view profile item
        #    temp_menu.append(Gtk.SeparatorMenuItem())
        #    item = Gtk.MenuItem(i18n.get('view_profile'))
        #    item.connect('activate', self.__save_column, acc.id_)
        #    temp_menu.append(item)
        #    temp.set_sensitive(False)
        #    self.menu.append(temp)

        #    empty = False

        #if empty:
        #    
        #else:
        #    self.menu.append(Gtk.SeparatorMenuItem())
        #self.menu.show_all()
        #self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

    #================================================================
    # Hooks definitions
    #================================================================

    def after_delete_account(self):
        self.account_deleted.emit()

    def after_delete_column(self, column_id):
        self._container.remove_column(column_id)
        if len(self.get_registered_columns()) == 0:
            self.dock.empty()
            self.tray.empty()
        # TODO: Enable timers
        #self.__remove_timer(column_id)

    '''
    def closeEvent(self, event):
        if self.unitylauncher.is_supported():
            self.showMinimized()
        else:
            self.hide()
        print self.ignore_quit
        if self.ignore_quit:
            event.ignore()

    def show_about(self):
        about = About(self)

    def show_preferences(self, widget=None):
        pref = Preferences(self)

    def show_accounts_dialog(self, widget=None):
        #self.accountsdlg.show()
        pass

    def show_update_box(self, widget=None):
        self.container.execute("show_update_box()")

    def show_update_box_for_direct(self, widget=None):
        self.container.execute("show_autocomplete_for_direct()")

    def __size_request(self, widget, rectangle):
        width = rectangle.width
        columns = len(self.core.all_registered_columns())
        preferred_width = MIN_WINDOW_WIDTH * columns
        if width < preferred_width:
            width = preferred_width
        self.save_window_geometry(width, rectangle.height)

    def __link_request(self, url):
        import webbrowser
        webbrowser.open(str(url)[1:])
        #self.open_url(url.toString())

    def __on_trayicon_click(self, widget):
        if self.showed:
            self.showed = False
            self.hide()
        else:
            self.showed = True
            self.show()

    def __on_main_indicator_clicked(self, indicator):
        self.showed = True
        self.show()
        self.present()

    def __on_indicator_clicked(self, indicator, data):
        self.indicator.clean()
        self.__on_main_indicator_clicked(indicator)

    def _eventFilter__manage_focus(self, event, focus):
        self.focus = focus
        if not self.focus:
            return
        self.unitylauncher.set_count_visible(False)
        self.unitylauncher.set_count(0)

    def __on_key_press(self, widget, event):
        """keyname = gtk.gdk.keyval_name(event.keyval)
        if (event.state & gtk.gdk.CONTROL_MASK) and keyname.lower() == 'n':
            self.show_update_box()
            return True
        return False"""
        pass

    def _link_request(self, url):
        self.on_link_request(url)

    def _action_request(self, url):
        self.on_action_request(url)

    def __show_tray_menu(self, widget, button, activate_time):
        """menu = gtk.Menu()
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
        menu.popup(None, None, None, button, activate_time)"""
        pass

    def __show_add_column_menu(self):
        self.menu = QtGui.QMenu("yay") 

        #empty = True
        twitter_public_acc = None
        identica_public_acc = None
        accounts = self.get_all_accounts()
        columns = self.get_all_columns()
        reg_columns = self.get_registered_columns()
        self.functions = []
        self.temps = []

        for acc in accounts:
            if acc.protocol_id == 'twitter' and twitter_public_acc is None:
                twitter_public_acc = acc.id_
            if acc.protocol_id == 'identica' and identica_public_acc is None:
                identica_public_acc = acc.id_
            name = "%s (%s)" % (acc.username, i18n.get(acc.protocol_id))

            self.temp = QtGui.QMenu(name)
            self.temps.append(self.temp)

            if acc.logged_in:
                temp_menu = QtGui.QMenu()
                for key, col in columns[acc.id_].iteritems():
                    f = function_caller(self.__add_column,col.build_id())
                    self.functions.append(f)
                    self.temp.addAction(key,self.functions[-1].call)
            else:
                pass
            self.menu.addMenu(self.temps[-1])
            empty = False

        self.public_tl = QtGui.QMenu(i18n.get('public_timeline'))
        self.public_tl_menu = QtGui.QMenu("menu")

        if twitter_public_acc:
            public_acc = twitter_public_acc + '-public'
            self.public_tl_menu.addAction(i18n.get('twitter'),self.__add_column,public_acc)

        if identica_public_acc:
            public_acc = identica_public_acc + '-public'
            self.public_tl_menu.addAction(i18n.get('twitter'),self.__add_column,public_acc)


        self.public_tl.addMenu(self.public_tl_menu)

        self.menu.addMenu(self.public_tl)
        self.menu.popup(QtGui.QCursor.pos())

    def __add_column(self,column_id):
        return self.save_column(column_id)

    def __close(self, widget, event=None):
        if self.core.minimize_on_close():
            self.showed = False
        else:
            self.main_quit(widget)
        return True

    def __timeout_callback(self, l):
        funct, arg, user_data = l
        if user_data:
            funct(arg,user_data)
            pass
        else:
            funct(arg)
            pass

    def _login_callback(self, arg, account_id):
        if arg.code > 0:
            msg = arg.errmsg
            self.show_notice(msg, 'error')
            self.accountsdlg.cancel_login(msg)
            return

        auth_obj = arg.items
        if auth_obj.must_auth():
            #self.accountsdlg.show()
            #self.accountsdlg.set_account_id(account_id)
            #self.accountsdlg.show_auth_win(auth_obj.url)
            pass
        else:
            self.__auth_callback(arg, account_id, False)

    def _AccountsDialog__oauth_callback(self, verifier, account_id):
        self.__oauth_callback(verifier,account_id)

    def __oauth_callback(self, verifier, account_id):
        self.worker.register(self.core.authorize_oauth_token, (account_id, verifier), self.__auth_callback, account_id)

    def __cancel_callback(self, widget, reason, account_id):
        self.delete_account(account_id)
        #self.accountsdlg.cancel_login(i18n.get(reason))

    def __auth_callback(self, arg, account_id, register = True):
        if arg.code > 0:
            msg = arg.errmsg
            self.show_notice(msg, 'error')
            #self.accountsdlg.cancel_login(msg)
        else:
            self.worker.register(self.core.auth, (account_id), self.__done_callback, (account_id, register))

    def __done_callback(self, arg, userdata):
        (account_id, register) = userdata

        if arg.code > 0:
            self.core.change_login_status(account_id, LoginStatus.NONE)
            msg = arg.errmsg
            #self.accountsdlg.cancel_login(msg)
            self.show_notice(msg, 'error')
        else:
            if register:
                account_id = self.core.name_as_id(account_id)

            #self.accountsdlg.done_login()
            #self.accountsdlg.update()

            response = self.core.get_own_profile(account_id)
            if response.code > 0:
                self.show_notice(response.errmsg, 'error')
            else:
                pass

            registered_var = self.get_registered_columns()
                
            for col in registered_var:
                if col.account_id == account_id:
                    self.download_stream(col, True)
                    self.__add_timer(col)
            self.resize(300*len(registered_var),480)


    def __add_timer(self, column):
        interval = self.core.get_update_interval()
        self.log.debug('--Creating timer for %s every %i min' % (column.id_, interval))
        self.timer = TimerExecution(self.download_stream,column) 
        self.ctimer = QtCore.QTimer()
        self.newtimers.append(self.timer)
        self.ctimer.timeout.connect(self.newtimers[-1].execute)
        self.ctimer.start(int(interval*1000*60))
        self.alltimers.append(self.ctimer)

        self.log.debug('--Created timer for %s every %i min (%f) msec' % (column.id_, interval,interval*1000*60))

    def __remove_timer(self, column_id):
        if self.timers.has_key(column_id):
            self.log.debug('--Removed timer for %s' % column_id)


    def show_about(self):
        #self.accountsdlg.show()
        #self.accountsdlg.show_about_win()
        pass

    def show_preferences(self):
        pref = Preferences(self)

    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------




    def profile_image_response(self, response):
        if response.code > 0:
            self.container.execute('hide_imageview(); show_notice("' + response.errmsg + '", "error");')
        else:
            pix = self.load_image(response.items, True)
            width = pix.width()
            height = pix.height()
            del pix
            cmd = "update_imageview('%s',%s,%s);" % (response.items, width, height)
            self.container.execute(cmd)

    def show_media_response(self, response):
        if response.err:
            self.container.execute('hide_imageview(); show_notice("' + response.errmsg + '", "error");')
        else:
            content_obj = response.response
            if content_obj.is_image():
                content_obj.save_content()
                #pix = gtk.gdk.pixbuf_new_from_file(content_obj.path)
                pix = QtGui.QPixmap(content_obj.path) 
                cmd = "update_imageview('%s',%s,%s);" % (
                    content_obj.path, pix.get_width(), pix.get_height())
                del pix
            elif content_obj.is_video() or content_obj.is_map():
                cmd = "update_videoview('%s',%s,%s);" % (
                    content_obj.path, content_obj.info['width'], content_obj.info['height'])
            self.container.execute(cmd)
    '''

    def update_column(self, arg, data):
        column, notif, max_ = data

        # Notifications
        # FIXME
        count = len(arg)

        if count > 0:
            self._container.update_column(column.id_, arg)

    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------

    def download_stream(self, column, notif=True):
        if self._container.is_updating(column.id_):
            return True

        last_id = self._container.start_updating(column.id_)
        count = self.core.get_max_statuses_per_column()

        self.worker.register(self.core.get_column_statuses, (column.account_id,
            column.slug, count, last_id), self.update_column,
            (column, notif, count))
        return True


    '''
    def refresh_column(self, column_id):
        for col in self.get_registered_columns():
            if col.build_id() == column_id:
                self.download_stream(col)

    def is_active(self):
        return self.focus
    '''

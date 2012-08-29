# -*- coding: utf-8 -*-

# Qt main view for Turpial
#
# Author: Carlos Guerrero and Andrea Stagi
# Sep 03, 2011

# PyQt4 Support:
from PyQt4 import QtCore, QtGui
from PyQt4.QtWebKit import *
from PyQt4.QtCore import pyqtSignal

from turpial.ui.base import *

from turpial.ui.qt.worker import Worker
from turpial.ui.qt.htmlview import HtmlView
from turpial.ui.qt.oauthwin import OAuthWindow
from turpial.ui.qt.accounts import AccountsDialog


# TODO: Improve all splits for accounts_id with a common function


class TimerExecution(object):
    def __init__(self, function, arg):
        self.function = function
        self.arg = arg

    def execute(self):
        self.function(self.arg)
        return True


class function_caller(object):
    def __init__(self,func,arg):
        print "inicializando",func,arg
        self.func = func
        self.arg = arg

    def call(self):
        print "ejecutando call"
        self.func(self.arg)

class function_caller2(object):
    def __init__(self,func,arg1,arg2):
        print "inicializando caller2",func,arg1,arg2
        self.func = func
        self.arg1 = arg1
        self.arg2 = arg1

    def call(self):
        print "ejecutando call"
        self.func(self.arg1,self.arg2)



class Main(Base, Singleton, QtGui.QMainWindow):

    emitter = pyqtSignal(list)

    def __init__(self, core):
        Singleton.__init__(self)
        Base.__init__(self, core)
        import sys
        self.app = QtGui.QApplication(sys.argv)
        self.focus = False
        QtGui.QMainWindow.__init__(self)

        class eventFilter(QtCore.QObject):
            def __init__(self, parent):
                super(eventFilter, self).__init__(parent)
            def eventFilter(self, object, event):
                if event.type() == 24:
                    object.__manage_focus(event, True)
                if event.type() == 25:
                    object.__manage_focus(event, False)
                return False

        self.filter = eventFilter(self)
        self.installEventFilter(self.filter)


        self.log = logging.getLogger('Qt')
        self.htmlparser = HtmlParser()
        self.setWindowTitle('Turpial')

        self.ignore_quit = True

        columns = self.get_all_columns()

        self.resize(310, 480)
        self.container = HtmlView()
        self.setCentralWidget(self.container.view)
        self.container.action_request.connect(self._action_request)
        self.container.link_request.connect(self._link_request)

        # TODO: Improve the use of this mode
        self.mode = 0

#        self.screen_width = self.get_screen().get_width()
        self.screen_width = 310 
        self.max_columns = self.screen_width / MIN_WINDOW_WIDTH

        # Configuration
        self.showed = True
        self.minimize = 'on'

        self.timers = {}
        self.newtimers = [] 
        self.alltimers = []
        self.updating = {}
        self.columns = {}

        self.sound = Sound()
#        self.notify = Notification()

        self.openstatuses = {}

        self.worker = Worker(self.emitter)
        self.emitter.connect(self.__timeout_callback)
        self.worker.start()

        # Persistent dialogs
        self.accountsdlg = AccountsDialog(self)
        self.accountsdlg.update()

        self.show()

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
        self.accountsdlg.show()

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
    def __create_trayicon(self):
        """if gtk.check_version(2, 10, 0) is not None:
            self.log.debug("Disabled Tray Icon. It needs PyGTK >= 2.10.0")
            return
        self.tray = gtk.StatusIcon()
        self.tray.set_from_pixbuf(self.load_image('turpial-tray.png', True))
        self.tray.set_tooltip('Turpial')
        self.tray.connect("activate", self.__on_trayicon_click)
        self.tray.connect("popup-menu", self.__show_tray_menu)"""
        pass

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
            self.accountsdlg.show()
            self.accountsdlg.set_account_id(account_id)
            self.accountsdlg.show_auth_win(auth_obj.url)
        else:
            self.__auth_callback(arg, account_id, False)

    def _AccountsDialog__oauth_callback(self, verifier, account_id):
        self.__oauth_callback(verifier,account_id)

    def __oauth_callback(self, verifier, account_id):
        self.worker.register(self.core.authorize_oauth_token, (account_id, verifier), self.__auth_callback, account_id)

    def __cancel_callback(self, widget, reason, account_id):
        self.delete_account(account_id)
        self.accountsdlg.cancel_login(i18n.get(reason))

    def __auth_callback(self, arg, account_id, register = True):
        if arg.code > 0:
            msg = arg.errmsg
            self.show_notice(msg, 'error')
            self.accountsdlg.cancel_login(msg)
        else:
            self.worker.register(self.core.auth, (account_id), self.__done_callback, (account_id, register))

    def __done_callback(self, arg, userdata):
        (account_id, register) = userdata

        if arg.code > 0:
            self.core.change_login_status(account_id, LoginStatus.NONE)
            msg = arg.errmsg
            self.accountsdlg.cancel_login(msg)
            self.show_notice(msg, 'error')
        else:
            if register:
                account_id = self.core.name_as_id(account_id)

            self.accountsdlg.done_login()
            self.accountsdlg.update()

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


    def load_image(self, path, pixbuf=False):
        img_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', '..', 'data', 'pixmaps', path))
        """pix = gtk.gdk.pixbuf_new_from_file(img_path)
        pix_file = QtCore.QFile(img_path) 
        pix = pix_file.readAll() 
        if pixbuf:
            return pix
        avatar = QtGui.QImage(pic)
        avatar.fromData(pix)
        del pix"""
        avatar = QtGui.QPixmap(img_path)
        return avatar

    def main_quit(self, widget=None, force=False):
        print "Exiting..."
        self.log.debug('Exiting...')
        self.unitylauncher.quit()
        self.tray = None
        self.ignore_quit = False
        self.worker.quit()
        self.destroy()

    def main_loop(self):
        self.app.exec_()
        self.app.quit()

    def show_main(self):
        reg_columns = self.get_registered_columns()
        if len(reg_columns) == 0:
            page = self.htmlparser.empty()
        else:
            page = self.htmlparser.main(self.get_accounts_list(), reg_columns)
        self.container.render(page)
        self.login()

    def show_about(self):
        self.accountsdlg.show()
        self.accountsdlg.show_about_win()

    def show_preferences(self):
        pref = Preferences(self)

    def login(self):
        #if self.core.play_sounds_in_login():
        #    self.sound.login()

        for acc in self.get_accounts_list():
            self.single_login(acc)

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

    # ------------------------------------------------------------
    # Timer Methods
    # ------------------------------------------------------------

    def download_stream(self, column, notif=True):
        for each in self.alltimers:
            print each, each.isActive()


        if self.updating.has_key(column.id_):
            if self.updating[column.id_]:
                return True
        else:
            self.updating[column.id_] = True

        if not self.columns.has_key(column.id_):
            self.columns[column.id_] = {'last_id': None}

        last_id = self.columns[column.id_]['last_id']
        num_statuses = self.core.get_max_statuses_per_column()
        self.container.execute("start_updating_column('" + column.id_ + "');")
        self.worker.register(self.core.get_column_statuses, (column.account_id,
            column.column_name, num_statuses, last_id), self.update_column, 
            (column, notif, num_statuses))
#        rtn = self.core.get_column_statuses(column.account_id,column.column_name,num_statuses)
#        self.update_column(rtn, (column, notif, num_statuses))
        return True

    def refresh_column(self, column_id):
        for col in self.get_registered_columns():
            if col.build_id() == column_id:
                self.download_stream(col)

    def is_active(self):
        return self.focus


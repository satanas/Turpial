# -*- coding: utf-8 -*-

# GTK main view for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Sep 03, 2011

import gtk
import gobject

from turpial.ui.base import *

from turpial.ui.gtk.about import About
from turpial.ui.gtk.worker import Worker
from turpial.ui.gtk.htmlview import HtmlView
from turpial.ui.gtk.indicator import Indicators
from turpial.ui.gtk.oauthwin import OAuthWindow
from turpial.ui.gtk.accounts import AccountsDialog
from turpial.ui.gtk.preferences import Preferences

gtk.gdk.set_program_class("Turpial")
gtk.gdk.threads_init()

# TODO: Improve all splits for accounts_id with a common function

class Main(Base, Singleton, gtk.Window):
    def __init__(self, core):
        Singleton.__init__(self)
        Base.__init__(self, core)
        gtk.Window.__init__(self)

        self.log = logging.getLogger('Gtk')
        self.htmlparser = HtmlParser()
        self.set_title('Turpial')
        self.set_size_request(310, 480)
        self.set_default_size(310, 480)
        self.set_icon(self.load_image('turpial.svg', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        self.connect('key-press-event', self.__on_key_press)
        self.connect('focus-in-event', self.__on_focus)
        #self.connect('size-request', self.__size_request)

        self.container = HtmlView()
        self.container.connect('action-request', self._action_request)
        self.container.connect('link-request', self._link_request)
        self.add(self.container)

        # TODO: Improve the use of this mode
        self.mode = 0

        self.screen_width = self.get_screen().get_width()
        self.max_columns = self.screen_width / MIN_WINDOW_WIDTH

        # Configuration
        self.showed = True
        self.minimize = 'on'

        self.timers = {}
        self.updating = {}
        self.columns = {}

        self.indicator = Indicators()
        self.indicator.connect('main-clicked', self.__on_main_indicator_clicked)
        self.indicator.connect('indicator-clicked', self.__on_indicator_clicked)

        self.openstatuses = {}

        self.worker = Worker()
        self.worker.set_timeout_callback(self.__timeout_callback)
        self.worker.start()

        # Persistent dialogs
        self.accountsdlg = AccountsDialog(self)
        self.__create_trayicon()

        self.show_all()

    def __size_request(self, widget, rectangle):
        ##print rectangle.width, rectangle.height, self.max_columns
        width = rectangle.width
        columns = len(self.core.all_registered_columns())
        preferred_width = MIN_WINDOW_WIDTH * columns
        if width < preferred_width:
            width = preferred_width
        ##print width, rectangle.width, preferred_width
        #self.set_default_size(width, rectangle.height)
        self.save_window_geometry(width, rectangle.height)

    def __create_trayicon(self):
        if gtk.check_version(2, 10, 0) is not None:
            self.log.debug("Disabled Tray Icon. It needs PyGTK >= 2.10.0")
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

    def __on_main_indicator_clicked(self, indicator):
        self.showed = True
        self.show()
        self.present()

    def __on_indicator_clicked(self, indicator, data):
        self.indicator.clean()
        self.__on_main_indicator_clicked(indicator)

    def __on_focus(self, widget, event):
        try:
            self.set_urgency_hint(False)
            self.unitylauncher.set_count_visible(False)
            self.unitylauncher.set_count(0)
        except Exception:
            pass
        self.tray.set_from_pixbuf(self.load_image('turpial-tray.png', True))

    def __on_key_press(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if (event.state & gtk.gdk.CONTROL_MASK) and keyname.lower() == 'n':
            self.show_update_box()
            return True
        return False

    def _link_request(self, widget, url):
        self.on_link_request(url)

    def _action_request(self, widget, url):
        self.on_action_request(url)

    def __show_tray_menu(self, widget, button, activate_time):
        menu = gtk.Menu()
        tweet = gtk.MenuItem(i18n.get('new_tweet'))
        direct = gtk.MenuItem(i18n.get('direct_message'))
        accounts = gtk.MenuItem(i18n.get('accounts'))
        prefs = gtk.MenuItem(i18n.get('preferences'))
        sound_ = gtk.CheckMenuItem(i18n.get('enable_sounds'))
        sound_.set_active(not self.sound._disable)
        exit_ = gtk.MenuItem(i18n.get('exit'))
        menu.append(tweet)
        menu.append(direct)
        menu.append(accounts)
        menu.append(prefs)
        menu.append(sound_)
        menu.append(gtk.SeparatorMenuItem())
        menu.append(exit_)

        tweet.connect('activate', self.show_update_box)
        direct.connect('activate', self.show_update_box_for_direct)
        accounts.connect('activate', self.show_accounts_dialog)
        prefs.connect('activate', self.show_preferences)
        sound_.connect('toggled', self.disable_sound)
        exit_.connect('activate', self.main_quit)

        menu.show_all()
        menu.popup(None, None, None, button, activate_time)

    def show_column_menu(self):
        menu = gtk.Menu()

        search = gtk.MenuItem(i18n.get('search'))
        search_menu = gtk.Menu()
        search_menu.append(gtk.MenuItem(i18n.get('twitter')))
        search_menu.append(gtk.MenuItem(i18n.get('identica')))
        search.set_submenu(search_menu)

        empty = True
        twitter_public_acc = None
        identica_public_acc = None
        accounts = self.get_all_accounts()
        columns = self.get_all_columns()
        reg_columns = self.get_registered_columns()

        for acc in accounts:
            if acc.protocol_id == 'twitter' and twitter_public_acc is None:
                twitter_public_acc = acc.id_
            if acc.protocol_id == 'identica' and identica_public_acc is None:
                identica_public_acc = acc.id_
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

        public_tl = gtk.MenuItem(i18n.get('public_timeline'))
        public_tl_menu = gtk.Menu()
        public_tl.set_submenu(public_tl_menu)

        if twitter_public_acc:
            public_acc = twitter_public_acc + '-public'
            twitter_public_tl = gtk.MenuItem(i18n.get('twitter'))
            twitter_public_tl.connect('activate', self.__add_column, public_acc)
            public_tl_menu.append(twitter_public_tl)
            for reg in reg_columns:
                if twitter_public_acc == reg.account_id and reg.column_name == 'public':
                    twitter_public_tl.set_sensitive(False)

        if identica_public_acc:
            public_acc = identica_public_acc + '-public'
            identica_public_tl = gtk.MenuItem(i18n.get('identica'))
            identica_public_tl.connect('activate', self.__add_column, public_acc)
            public_tl_menu.append(identica_public_tl)
            for reg in reg_columns:
                if identica_public_acc == reg.account_id and reg.column_name == 'public':
                    identica_public_tl.set_sensitive(False)

        if empty:
            empty_menu = gtk.MenuItem(i18n.get('no_registered_accounts'))
            empty_menu.set_sensitive(False)
            menu.append(empty_menu)
        else:
            menu.append(gtk.SeparatorMenuItem())
            menu.append(public_tl)
            menu.append(search)
        menu.show_all()
        menu.popup(None, None, None, 0, gtk.get_current_event_time())

    def __add_column(self, widget, column_id):
        self.save_column(column_id)

    def show_profile_menu(self):
        menu = gtk.Menu()
        accounts = self.get_all_accounts()
        twitter_acc = None
        identica_acc = None


        profile = gtk.MenuItem(i18n.get('view_my_profile'))
        profile_menu = gtk.Menu()
        for acc in accounts:
            if acc.protocol_id == 'twitter' and twitter_acc is None:
                twitter_acc = acc.id_
            if acc.protocol_id == 'identica' and identica_acc is None:
                identica_acc = acc.id_
            name = "%s (%s)" % (acc.username, i18n.get(acc.protocol_id))
            item = gtk.MenuItem(name)
            item.connect('activate', self.__show_profile, acc.id_, acc.username)
            profile_menu.append(item)
        profile.set_submenu(profile_menu)
        menu.append(profile)

        menu.append(gtk.SeparatorMenuItem())

        tsearch = gtk.MenuItem(i18n.get('twitter'))
        tsearch.connect('activate', self.__search_profile, twitter_acc)

        isearch = gtk.MenuItem(i18n.get('identica'))
        isearch.connect('activate', self.__search_profile, identica_acc)

        search = gtk.MenuItem(i18n.get('search_profile_in'))
        search_menu = gtk.Menu()
        search_menu.append(tsearch)
        search_menu.append(isearch)
        search.set_submenu(search_menu)

        menu.append(search)
        menu.show_all()
        menu.popup(None, None, None, 0, gtk.get_current_event_time())

    def show_repeat_menu(self, args):
        menu = gtk.Menu()

        retweet = gtk.MenuItem(i18n.get('retweet'))
        retweet.connect('activate', self.__perform_retweet, args)
        quote = gtk.MenuItem(i18n.get('quote'))
        quote.connect('activate', self.__perform_quote, args)

        menu.append(retweet)
        menu.append(quote)

        menu.show_all()
        menu.popup(None, None, None, 0, gtk.get_current_event_time())

    def __perform_retweet(self, widget, args):
        cmd = ARG_SEP.join([args[0], args[1]])
        cmd2 = "show_confirm_window('%s', '%s', 'cmd:repeat_status:%s')" % (
            i18n.get('confirm_retweet'), i18n.get('do_you_want_to_retweet'), cmd)
        self.container.execute(cmd2)

    def __perform_quote(self, widget, args):
        cmd = "quote_status('%s','%s','%s')" % (args[0], args[2], args[3])
        self.container.execute(cmd)

    def __show_profile(self, widget, acc_id, username):
        self.show_profile(acc_id, username)

    def __search_profile(self, widget, acc_id):
        cmd = "show_autocomplete_for_profile('%s')" % acc_id
        self.container.execute(cmd)

    def __close(self, widget, event=None):
        if self.core.minimize_on_close():
            self.showed = False
            if self.unitylauncher.is_supported():
                self.iconify()
            else:
                self.hide()
        else:
            self.main_quit(widget)
        return True

    def __timeout_callback(self, funct, arg, user_data):
        if user_data:
            gobject.timeout_add(200, funct, arg, user_data)
        else:
            gobject.timeout_add(200, funct, arg)

    def _login_callback(self, arg, account_id):
        if arg.code > 0:
            msg = arg.errmsg
            self.show_notice(msg, 'error')
            self.accountsdlg.cancel_login(msg)
            return

        self.accountsdlg.status_message(i18n.get('authenticating'))
        auth_obj = arg.items
        if auth_obj.must_auth():
            oauthwin = OAuthWindow(self, self.accountsdlg.form, account_id)
            oauthwin.connect('response', self.__oauth_callback)
            oauthwin.connect('cancel', self.__cancel_callback)
            oauthwin.open(auth_obj.url)
        else:
            self.__auth_callback(arg, account_id, False)

    def __oauth_callback(self, widget, verifier, account_id):
        self.accountsdlg.status_message(i18n.get('authorizing'))
        self.worker.register(self.core.authorize_oauth_token, (account_id, verifier), self.__auth_callback, account_id)

    def __cancel_callback(self, widget, reason, account_id):
        #self.delete_account(account_id)
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
                if self.core.show_notifications_in_login():
                    self.notify.login(response.items)

            for col in self.get_registered_columns():
                if col.account_id == account_id:
                    self.download_stream(col, True)
                    self.__add_timer(col)


    def __add_timer(self, column):
        #if (self.timer1 != home_interval):
        if self.timers.has_key(column.id_):
            gobject.source_remove(self.timers[column.id_])
        interval = self.core.get_update_interval()
        self.timers[column.id_] = gobject.timeout_add(interval * 60 * 1000,
            self.download_stream, column)
        self.log.debug('--Created timer for %s every %i min' % (column.id_, interval))

    def __remove_timer(self, column_id):
        if self.timers.has_key(column_id):
            gobject.source_remove(self.timers[column_id])
            self.log.debug('--Removed timer for %s' % column_id)

    def load_image(self, path, pixbuf=False):
        img_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', '..', 'data', 'pixmaps', path))
        pix = gtk.gdk.pixbuf_new_from_file(img_path)
        if pixbuf:
            return pix
        avatar = gtk.Image()
        avatar.set_from_pixbuf(pix)
        del pix
        return avatar

    def main_quit(self, widget=None, force=False):
        self.log.debug('Exiting...')
        self.unitylauncher.quit()
        self.destroy()
        self.tray = None
        self.worker.quit()
        self.worker.join()
        if widget:
            gtk.main_quit()
        if force:
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

    def show_preferences(self, widget=None):
        pref = Preferences(self)

    def show_accounts_dialog(self, widget=None):
        self.accountsdlg.show()

    def show_update_box(self, widget=None):
        self.deiconify()
        self.show()
        self.present()
        self.container.execute("show_update_box()")

    def show_update_box_for_direct(self, widget=None):
        self.deiconify()
        self.show()
        self.present()
        self.container.execute("show_autocomplete_for_direct()")

    def login(self):
        if self.core.play_sounds_in_login():
            self.sound.login()

        for acc in self.get_accounts_list():
            self.single_login(acc)

        self.worker.register(self.core.load_all_friends_list, (), self.load_all_friends_response)

    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------

    def profile_image_response(self, response):
        if response.code > 0:
            self.container.execute('hide_imageview(); show_notice("' + response.errmsg + '", "error");')
        else:
            pix = self.load_image(response.items, True)
            width = pix.get_width()
            height = pix.get_height()
            del pix
            cmd = "update_imageview('%s',%s,%s);" % (response.items, width, height)
            self.container.execute(cmd)

    def show_media_response(self, response):
        if response.err:
            self.container.execute('hide_imageview(); show_notice("' + response.errmsg + '", "error");')
        else:
            content_obj = response.response
            if content_obj.is_image():
                print "content_obj", content_obj.path
                content_obj.save_content()
                pix = gtk.gdk.pixbuf_new_from_file(content_obj.path)
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
        return True

    def refresh_column(self, column_id):
        for col in self.get_registered_columns():
            if col.build_id() == column_id:
                self.download_stream(col)


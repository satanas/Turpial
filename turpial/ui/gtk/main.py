# -*- coding: utf-8 -*-

# GTK3 main view for Turpial

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf

from turpial import DESC
from turpial.ui.base import *
from turpial.ui.gtk.dock import Dock
from turpial.ui.gtk.tray import TrayIcon
from turpial.ui.gtk.worker import Worker
from turpial.ui.gtk.container import Container
from turpial.ui.gtk.imageview import ImageView
from turpial.ui.gtk.indicator import Indicators

# Dialogs
from turpial.ui.gtk.about import AboutDialog
from turpial.ui.gtk.oauth import OAuthDialog
from turpial.ui.gtk.updatebox import UpdateBox
from turpial.ui.gtk.accounts import AccountsDialog
from turpial.ui.gtk.preferences import PreferencesDialog

#gtk.gdk.set_program_class("Turpial")

GObject.threads_init()

# TODO: Improve all splits for accounts_id with a common function
class Main(Base, Gtk.Window):
    def __init__(self, core):
        Base.__init__(self, core)
        Gtk.Window.__init__(self)

        self.log = logging.getLogger('Gtk')
        self.set_title(DESC)
        self.set_size_request(250, 480)
        self.set_default_size(300, 480)
        self.set_icon(self.load_image('turpial.svg', True))
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_gravity(Gdk.Gravity.STATIC)
        self.connect('delete-event', self.__on_close)
        #self.connect('key-press-event', self.__on_key_press)
        self.connect('focus-in-event', self.__on_focus)
        #self.connect('size-request', self.__size_request)

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
        self.worker.set_timeout_callback(self.__worker_timeout_callback)
        self.worker.start()

        # Persistent dialogs
        self.about_dialog = AboutDialog(self)
        self.accounts_dialog = AccountsDialog(self)
        self.update_box = UpdateBox(self)
        self.preferences_dialog = PreferencesDialog(self)

        self.imageview = ImageView(self)

        self.tray = TrayIcon(self)
        self.tray.connect("activate", self.__on_tray_click)
        self.tray.connect("popup-menu", self.__show_tray_menu)

        self.dock = Dock(self)
        self._container = Container(self)

        vbox = Gtk.VBox()
        vbox.pack_start(self._container, True, True, 0)
        vbox.pack_start(self.dock, False, False, 0)
        self.add(vbox)

    def __on_close(self, widget, event=None):
        if self.core.minimize_on_close():
            self.showed = False
            if self.unitylauncher.is_supported():
                self.iconify()
            else:
                self.hide()
        else:
            self.main_quit(widget)
        return True

    #================================================================
    # Tray icon
    #================================================================

    def __on_tray_click(self, widget):
        if self.showed:
            self.showed = False
            self.hide()
        else:
            self.showed = True
            self.show()

    def __show_tray_menu(self, widget, button, activate_time):
        return self.tray.popup(button, activate_time)

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
        self.tray.clear()

    #================================================================
    # Overrided methods
    #================================================================

    def main_loop(self):
        try:
            Gdk.threads_enter()
            Gtk.main()
            Gdk.threads_leave()
        except Exception:
            sys.exit(0)

    def main_quit(self, widget=None, force=False):
        self.log.debug('Exiting...')
        self.unitylauncher.quit()
        self.destroy()
        self.tray = None
        self.worker.quit()
        self.worker.join()
        if widget:
            Gtk.main_quit()
        if force:
            sys.exit(0)

    def show_main(self):
        self.start()
        self.show_all()
        self.update_container()

    def show_notice(self, message, type_):
        pass

    def show_media(self, url):
        self.imageview.loading()
        self.worker.register(self.core.get_media_content, (url, None),
            self.__show_media_callback)

    def login(self, account_id):
        self.accounts_dialog.update()
        self.worker.register(self.core.login, (account_id), self.__login_callback, account_id)


    #================================================================
    # Hooks definitions
    #================================================================

    def after_delete_account(self, deleted, err_msg=None):
        self.accounts_dialog.done_delete()

    def after_save_account(self, account_id, err_msg=None):
        self.worker.register(self.core.login, (account_id), self.__login_callback, account_id)

    def after_save_column(self, column, err_msg=None):
        self._container.add_column(column)
        self.dock.normal()
        self.tray.normal()
        self.download_stream(column)
        #self.__add_timer(column)

    def after_delete_column(self, column_id, err_msg=None):
        self._container.remove_column(column_id)
        if len(self.get_registered_columns()) == 0:
            self.dock.empty()
            self.tray.empty()
        #self.__remove_timer(column_id)

    def after_login(self):
        #self.worker.register(self.core.load_all_friends_list, (), self.load_all_friends_response)
        pass

    #================================================================
    # Own methods
    #================================================================

    def load_image(self, path, pixbuf=False):
        img_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', '..', 'data', 'pixmaps', path))
        pix = GdkPixbuf.Pixbuf.new_from_file(img_path)
        if pixbuf:
            return pix
        avatar = Gtk.Image()
        avatar.set_from_pixbuf(pix)
        del pix
        return avatar

    def show_about_dialog(self, widget=None):
        self.about_dialog.show()

    def show_accounts_dialog(self, widget=None):
        self.accounts_dialog.show()

    def show_preferences_dialog(self, widget=None):
        self.preferences_dialog.show()

    def show_search_dialog(self, widget=None):
        pass

    def show_update_box(self, widget=None, direct=False):
        self.update_box.show_for_direct('satanas82-twitter', 'zeitan')

    def update_column(self, arg, data):
        column, notif, max_ = data
        self.log.debug('Updated column %s' % column.id_)

        if arg.code > 0:
            self._container.stop_updating(column.id_, arg.errmsg, 'error')
            return

        self._container.update_column(column.id_, arg.items)

        # Notifications
        # FIXME
        #count = len(arg.items)
        #if count != 0:
        #    if notif and self.core.show_notifications_in_updates():
        #        self.notify.updates(column, count)
        #    if self.core.play_sounds_in_updates():
        #        self.sound.updates()
        #    if not self.is_active():
        #        self.unitylauncher.increment_count(count)
        #        self.unitylauncher.set_count_visible(True)
        #    else:
        #        self.unitylauncher.set_count_visible(False)
        #column.inc_size(count)

        # self.restore_open_tweets() ???

    def update_container(self):
        columns = self.get_registered_columns()
        if len(columns) == 0:
            self._container.empty()
            self.dock.empty()
            self.tray.empty()
        else:
            self._container.normal(self.get_accounts_list(), columns)
            self.dock.normal()
            self.tray.normal()

    #================================================================
    # Callbacks
    #================================================================

    def __login_callback(self, arg, account_id):
        if arg.code > 0:
            # FIXME: Implemente notice
            # self.show_notice(arg.errmsg, 'error')
            self.accounts_dialog.cancel_login(arr.errmsg)
            return

        self.accounts_dialog.status_message(i18n.get('authenticating'))
        auth_obj = arg.items
        if auth_obj.must_auth():
            oauthwin = OAuthDialog(self, self.accounts_dialog.form, account_id)
            oauthwin.connect('response', self.__oauth_callback)
            oauthwin.connect('cancel', self.__cancel_callback)
            oauthwin.open(auth_obj.url)
        else:
            self.__auth_callback(arg, account_id, False)

    def __oauth_callback(self, widget, verifier, account_id):
        self.accounts_dialog.status_message(i18n.get('authorizing'))
        self.worker.register(self.core.authorize_oauth_token, (account_id, verifier), self.__auth_callback, account_id)

    def __cancel_callback(self, widget, reason, account_id):
        self.delete_account(account_id)
        self.accounts_dialog.cancel_login(i18n.get(reason))

    def __auth_callback(self, arg, account_id, register = True):
        if arg.code > 0:
            # FIXME: Implemente notice
            #self.show_notice(msg, 'error')
            self.accounts_dialog.cancel_login(arg.errmsg)
        else:
            self.worker.register(self.core.auth, (account_id), self.__done_callback, (account_id, register))

    def __done_callback(self, arg, userdata):
        (account_id, register) = userdata
        if arg.code > 0:
            self.core.change_login_status(account_id, LoginStatus.NONE)
            self.accounts_dialog.cancel_login(arg.errmsg)
            #self.show_notice(msg, 'error')
        else:
            if register:
                account_id = self.core.name_as_id(account_id)

            self.accounts_dialog.done_login()
            self.accounts_dialog.update()

            response = self.core.get_own_profile(account_id)
            if response.code > 0:
                #self.show_notice(response.errmsg, 'error')
                pass
            else:
                if self.core.show_notifications_in_login():
                    self.notify.login(response.items)

            for col in self.get_registered_columns():
                if col.account_id == account_id:
                    self.download_stream(col, True)
                    #self.__add_timer(col)

    def __show_media_callback(self, response):
        if response.err:
            self.imageview.error(response.errmsg)
        else:
            content_obj = response.response
            if content_obj.is_image():
                content_obj.save_content()
                self.imageview.update(content_obj.path)
            elif content_obj.is_video() or content_obj.is_map():
                self.imageview.error('Media not supported yet')

    def __worker_timeout_callback(self, funct, arg, user_data):
        if user_data:
            GObject.timeout_add(Worker.TIMEOUT, funct, arg, user_data)
        else:
            GObject.timeout_add(Worker.TIMEOUT, funct, arg)

    #================================================================
    # Timer Methods
    #================================================================

    def download_stream(self, column, notif=True):
        if self._container.is_updating(column.id_):
            return True

        last_id = self._container.start_updating(column.id_)
        count = self.core.get_max_statuses_per_column()

        self.worker.register(self.core.get_column_statuses, (column.account_id,
            column.column_name, count, last_id), self.update_column,
            (column, notif, count))
        return True

    def refresh_column(self, column_id):
        for col in self.get_registered_columns():
            if col.build_id() == column_id:
                self.download_stream(col)


"""
class Main2(Base, gtk.Window):
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

    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------

    def profile_image_response(self, response):
        if response.code > 0:
            self.imageview.error(response.errmsg)
        else:
            self.imageview.update(response.items)



"""

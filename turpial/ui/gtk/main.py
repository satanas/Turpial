# -*- coding: utf-8 -*-

# GTK3 main view for Turpial

import os
import urllib2

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
from turpial.ui.gtk.search import SearchDialog
from turpial.ui.gtk.updatebox import UpdateBox
from turpial.ui.gtk.profiles import ProfileDialog
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
        self.set_size_request(250, 250)
        self.set_default_size(300, 480)
        self.set_icon(self.load_image('turpial.svg', True))
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_gravity(Gdk.Gravity.STATIC)
        self.connect('delete-event', self.__on_close)
        self.connect('key-press-event', self.__on_key_press)
        self.connect('focus-in-event', self.__on_focus)
        #self.connect('size-request', self.__size_request)

        # Configuration
        self.showed = True
        self.minimize = 'on'
        self.is_fullscreen = False

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

        self.avatars_worker = Worker()
        self.avatars_worker.set_timeout_callback(self.__worker_timeout_callback)
        self.avatars_worker.start()

        # Persistent dialogs
        self.accounts_dialog = AccountsDialog(self)
        self.profile_dialog = ProfileDialog(self)
        self.update_box = UpdateBox(self)

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

    def __on_key_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname.upper() == 'F' and event.state & Gdk.ModifierType.CONTROL_MASK:
            self.__toogle_fullscreen()
            return True
        return False

    def __toogle_fullscreen(self):
        if self.is_fullscreen:
            self.unfullscreen()
            self.is_fullscreen = False
        else:
            self.fullscreen()
            self.is_fullscreen = True

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
        self.avatars_worker.quit()
        self.avatars_worker.join()
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

    def show_user_avatar(self, account_id, user):
        self.imageview.loading()
        self.worker.register(self.core.get_profile_image, (account_id, user),
            self.__show_user_avatar_callback)

    def show_user_profile(self, account_id, user):
        self.profile_dialog.loading()
        self.worker.register(self.core.get_user_profile, (account_id, user),
            self.__show_user_profile_callback)

    def login(self, account_id):
        #return
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
        self.__add_timer(column)

    def after_delete_column(self, column_id, err_msg=None):
        self._container.remove_column(column_id)
        if len(self.get_registered_columns()) == 0:
            self.dock.empty()
            self.tray.empty()
        self.__remove_timer(column_id)

    def after_login(self):
        #self.worker.register(self.core.load_all_friends_list, (), self.load_all_friends_response)
        pass

    def after_update_status(self, response, account_id):
        if response.code > 0:
            self.update_box.update_error(response.errmsg)
        else:
            self.update_box.done()

    def after_broadcast_status(self, response):
        bad_acc = []
        good_acc = []
        error = False
        for resp in response:
            if resp.code > 0:
                error = True
                protocol = i18n.get(resp.account_id.split('-')[1])
                bad_acc.append("%s (%s)" % (resp.account_id.split('-')[0], protocol))
            else:
                good_acc.append(resp.account_id)

        if error:
            self.update_box.broadcast_error(good_acc, bad_acc)
        else:
            self.update_box.done()

    def after_direct_message(self, response):
        if response.code > 0:
            self.update_box.update_error(response.errmsg)
        else:
            self.update_box.done()

    def after_favorite(self, response, action):
        # TODO: Check for errors
        if action == self.ACTION_FAVORITE:
            self._container.mark_status_favorite(response.items)
        else:
            self._container.unmark_status_favorite(response.items)

    def after_repeat(self, response, action):
        # TODO: Check for errors
        if action == self.ACTION_REPEAT:
            self._container.mark_status_repeat(response.items)
        else:
            self._container.unmark_status_repeat(response.items)

    def after_delete_status(self, response):
        if response.code > 0:
            # show notice
            # unlock status
            pass
        else:
            self._container.delete_status(response.items)

    def after_autoshort_url(self, response):
        self.update_box.update_after_short_url(response)

    #================================================================
    # Own methods
    #================================================================

    def load_image(self, filename, pixbuf=False):
        img_path = os.path.join(self.images_path, filename)
        pix = GdkPixbuf.Pixbuf.new_from_file(img_path)
        if pixbuf:
            return pix
        avatar = Gtk.Image()
        avatar.set_from_pixbuf(pix)
        del pix
        return avatar

    def show_about_dialog(self, widget=None):
        about_dialog = AboutDialog(self)
        about_dialog.show()

    def show_accounts_dialog(self, widget=None):
        self.accounts_dialog.show()

    def show_preferences_dialog(self, widget=None):
        preferences_dialog = PreferencesDialog(self)
        preferences_dialog.show()

    def show_search_dialog(self, widget=None):
        search_dialog = SearchDialog(self)
        search_dialog.show()

    def show_update_box(self, widget=None, direct=False):
        self.update_box.show()

    def show_update_box_for_reply(self, in_reply_id, account_id, in_reply_user):
        self.update_box.show_for_reply(in_reply_id, account_id, in_reply_user)

    def show_update_box_for_reply_direct(self, in_reply_id, account_id, in_reply_user):
        self.update_box.show_for_reply_direct(in_reply_id, account_id, in_reply_user)

    def show_update_box_for_quote(self, message):
        self.update_box.show_for_quote(message)

    def show_confirm_dialog(self, message, callback, *args):
        dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.MODAL,
            Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, message)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            callback(*args)

    def confirm_repeat_status(self, status):
        self.show_confirm_dialog(i18n.get('do_you_want_to_repeat_status'),
            self.repeat_status, status)

    def confirm_unrepeat_status(self, status):
        self.show_confirm_dialog(i18n.get('do_you_want_to_undo_repeat_status'),
            self.unrepeat_status, status)

    def confirm_favorite_status(self, status):
        self.favorite_status(status)

    def confirm_unfavorite_status(self, status):
        self.unfavorite_status(status)

    def confirm_delete_status(self, status):
        self.show_confirm_dialog(i18n.get('do_you_want_to_delete_status'),
            self.delete_status, status)

    def update_column(self, arg, data):
        column, notif, max_ = data

        if arg.code > 0:
            self._container.stop_updating(column.id_, arg.errmsg, 'error')
            print arg.errmsg
            return

        # Notifications
        # FIXME
        count = len(arg.items)

        if count > 0:
            self.log.debug('Updated %s statuses in column %s' % (count, column.id_))
            self._container.update_column(column.id_, arg.items)
        else:
            self.log.debug('Column %s not updated' % column.id_)
            self._container.stop_updating(column.id_)
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

    def fetch_status_avatar(self, status, callback):
        self.worker.register(self.core.get_status_avatar, (status),
            callback)

    #================================================================
    # Callbacks
    #================================================================

    def __login_callback(self, arg, account_id):
        if arg.code > 0:
            # FIXME: Implemente notice
            # self.show_notice(arg.errmsg, 'error')
            self.accounts_dialog.cancel_login(arg.errmsg)
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
                    self.__add_timer(col)

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

    def __show_user_avatar_callback(self, response):
        if response.code > 0:
            self.imageview.error(response.errmsg)
        else:
            self.imageview.update(response.items)

    def __show_user_profile_callback(self, response):
        if response.code > 0:
            self.profile_dialog.error(response.errmsg)
        else:
            self.profile_dialog.update(response.items)

    def __worker_timeout_callback(self, funct, arg, user_data):
        if user_data:
            GObject.timeout_add(Worker.TIMEOUT, funct, arg, user_data)
        else:
            GObject.timeout_add(Worker.TIMEOUT, funct, arg)

    #================================================================
    # Timer Methods
    #================================================================

    def __add_timer(self, column):
        self.__remove_timer(column.id_)

        interval = self.core.get_update_interval()
        self.timers[column.id_] = GObject.timeout_add(interval * 60 * 1000,
            self.download_stream, column)
        self.log.debug('--Created timer for %s every %i min' % (column.id_, interval))

    def __remove_timer(self, column_id):
        if self.timers.has_key(column_id):
            GObject.source_remove(self.timers[column_id])
            self.log.debug('--Removed timer for %s' % column_id)

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

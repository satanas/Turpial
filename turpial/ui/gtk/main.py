# -*- coding: utf-8 -*-

# GTK main view for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Sep 03, 2011

import os
import gtk
import sys
import base64
import urllib
import gobject
import logging

from xml.sax.saxutils import unescape

from libturpial.common import *

from turpial.ui.base import *
from turpial.ui.lang import i18n
from turpial.ui.sound import Sound
from turpial.ui.html import HtmlParser
from turpial.ui.gtk.about import About
from turpial.singleton import Singleton
from turpial.ui.gtk.worker import Worker
from turpial.ui.gtk.htmlview import HtmlView
from turpial.notification import Notification
from turpial.ui.gtk.indicator import Indicators
from turpial.ui.gtk.oauthwin import OAuthWindow
from turpial.ui.gtk.accounts import AccountsDialog

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
        self.connect('size-request', self.__size_request)
        
        self.container = HtmlView()
        self.container.connect('action-request', self.__action_request)
        self.container.connect('link-request', self.__link_request)
        self.add(self.container)
        
        # TODO: Improve the use of this mode
        self.mode = 0
        
        self.screen_width = self.get_screen().get_width()
        self.max_columns = self.screen_width / MIN_WINDOW_WIDTH
        
        # Configuration
        self.showed = True
        self.minimize = 'on'
        
        self.timers = {}
        self.interval1 = -1
        self.interval2 = -1
        self.interval3 = -1
        
        self.updating = {}
        self.columns = {}
        
        self.sound = Sound()
        self.notify = Notification()
        self.indicator = Indicators()
        self.indicator.connect('main-clicked', self.__on_main_indicator_clicked)
        self.indicator.connect('indicator-clicked', self.__on_indicator_clicked)
        
        self.worker = Worker()
        self.worker.set_timeout_callback(self.__timeout_callback)
        self.worker.start()
        
        # Persistent dialogs
        self.accountsdlg = AccountsDialog(self)
        
        self.__create_trayicon()
        self.show_all()
    
    def __size_request(self, widget, rectangle):
        print rectangle.width, rectangle.height, self.max_columns
        width = rectangle.width
        columns = len(self.core.all_registered_columns())
        preferred_width = MIN_WINDOW_WIDTH * columns
        if width < preferred_width:
            width = preferred_width
        print width, rectangle.width, preferred_width
        #self.set_default_size(width, rectangle.height)
        self.save_window_geometry(width, rectangle.height)
    
    def __link_request(self, widget, url):
        self.open_url(url)
        
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
    
    def __login_callback(self, arg, account_id):
        if arg.code > 0:
            msg = arg.errmsg
            self.show_notice(msg, 'error')
            self.accountsdlg.cancel_login(msg)
            return
        
        auth_obj = arg.items
        if auth_obj.must_auth():
            oauthwin = OAuthWindow(self, self.accountsdlg.form, account_id)
            oauthwin.connect('response', self.__oauth_callback)
            oauthwin.connect('cancel', self.__cancel_callback)
            oauthwin.open(auth_obj.url)
        else:
            self.__auth_callback(arg, account_id)
    
    def __oauth_callback(self, widget, verifier, account_id):
        #self.form.set_loading_message(i18n.get('authorizing'))
        self.worker.register(self.core.authorize_oauth_token, (account_id, verifier), self.__auth_callback, account_id)
    
    def __cancel_callback(self, widget, reason, account_id):
        self.delete_account(account_id)
        self.accountsdlg.cancel_login(i18n.get(reason))
    
    def __auth_callback(self, arg, account_id):
        if arg.code > 0:
            msg = arg.errmsg
            self.show_notice(msg, 'error')
            self.accountsdlg.cancel_login(msg)
        else:
            self.worker.register(self.core.auth, (account_id), self.__done_callback, account_id)
    
    def __done_callback(self, arg, account_id):
        if arg.code > 0:
            self.core.change_login_status(account_id, LoginStatus.NONE)
            msg = arg.errmsg
            self.accountsdlg.cancel_login(msg)
            self.show_notice(msg, 'error')
        else:
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
        self.interval1 = 5
        self.timers[column.id_] = gobject.timeout_add(self.interval1 * 60 * 1000, 
            self.download_stream, column)
        self.log.debug('--Created timer for %s every %i min' % (column.id_, self.interval1))
    
    def __remove_timer(self, column_id):
        if self.timers.has_key(column_id):
            gobject.source_remove(self.timers[column_id])
            self.log.debug('--Removed timer for %s' % column_id)
    
    def __action_request(self, widget, url):
        action, args = self.htmlparser.parse_command(url)
        print action, args
        if action == 'about':
            self.show_about()
        elif action == 'preferences':
            self.container.execute("alert('hola');")
        elif action == 'accounts_manager':
            self.accountsdlg.show()
        elif action == 'add_column':
            self.__show_add_column_menu(widget)
        elif action == 'update_column':
            self.refresh_column(args[0])
        elif action == 'delete_column':
            self.delete_column(args[0])
        elif action == 'repeat_status':
            self.repeat_status(args[0], args[1])
        elif action == 'unrepeat_status':
            self.unrepeat_status(args[0], args[1])
        elif action == 'fav_status':
            self.fav_status(args[0], args[1])
        elif action == 'unfav_status':
            self.unfav_status(args[0], args[1])
        elif action == 'update_status':
            self.update_status(args[0], args[1])
        elif action == 'reply_status':
            self.reply_status(args[0], args[1], args[2])
        elif action == 'delete_status':
            self.delete_status(args[0], args[1])
        elif action == 'show_profile':
            self.show_profile(args[0], args[1])
        elif action == 'report_spam':
            self.report_spam(args[0], args[1])
        elif action == 'block':
            self.block(args[0], args[1])
        elif action == 'follow':
            self.follow(args[0], args[1])
        elif action == 'unfollow':
            self.unfollow(args[0], args[1])
        elif action == 'mute':
            self.mute(args[0])
        elif action == 'unmute':
            self.unmute(args[0])
        elif action == 'load_friends':
            self.load_friends()
        elif action == 'showreply':
            self.showreply(args[0], args[1], args[2])
        elif action == 'showconversation':
            self.showconversation(args[0], args[1])
        elif action == 'short_urls':
            self.short_urls(args[0])
        elif action == 'direct_message':
            self.direct_message(args[0], args[1], args[2])
        elif action == 'profile_image':
            self.profile_image(args[0], args[1])
    
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
        if pixbuf: 
            return pix
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
    
    def show_notice(self, msg, type_):
        cmd = 'show_notice("%s", "%s");' % (msg, type_)
        self.container.execute(cmd)
    
    def login(self):
        if self.core.play_sounds_in_notification():
            self.sound.login()
        
        for acc in self.get_accounts_list():
            self.single_login(acc)
    
    def single_login(self, acc):
        self.core.change_login_status(acc, LoginStatus.IN_PROGRESS)
        self.accountsdlg.update()
        self.worker.register(self.core.login, (acc), self.__login_callback, acc)
    
    def delete_account(self, account_id):
        reg_columns = self.get_registered_columns()
        for col in reg_columns:
            if col.account_id == account_id:
                self.delete_column(col.id_)
        self.core.unregister_account(account_id, True)
        self.accountsdlg.update()
    
    def save_account(self, username, protocol_id, password):
        account_id = self.core.register_account(username, protocol_id, password)
        self.worker.register(self.core.login, (account_id), self.__login_callback, account_id)
    
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
    
    def repeat_status(self, account_id, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('retweeting'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.repeat_status, (account_id, status_id), 
            self.repeat_response, (True, status_id))
    
    def unrepeat_status(self, account_id, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('unretweeting'))
        self.container.execute(cmd)

        self.worker.register(self.core.unrepeat_status, (account_id, status_id), 
                self.repeat_response, (False, status_id))
    
    def fav_status(self, account_id, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('adding_to_fav'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.mark_favorite, (account_id, status_id), 
            self.fav_response, True)
    
    def unfav_status(self, account_id, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('removing_from_fav'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.unmark_favorite, (account_id, status_id), 
            self.fav_response, False)
    
    def update_status(self, account, text):
        message = base64.b64decode(text)
        accounts = []
        for acc in account.split('|'):
            accounts.append(acc)
        
        if len(accounts) > 1:
            self.worker.register(self.core.broadcast_status, (accounts, message), 
                self.broadcast_status_response)
        else:
            self.worker.register(self.core.update_status, (accounts[0], message), 
                self.update_status_response, accounts[0])
    
    def reply_status(self, account, status_id, text):
        message = base64.b64decode(text)
        self.worker.register(self.core.update_status, (account, message, status_id), 
            self.update_status_response, account)
    
    def delete_status(self, account, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('deleting'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.destroy_status, (account, status_id), 
            self.delete_status_response)
    
    def show_profile(self, account_id, username):
        self.worker.register(self.core.get_user_profile, (account_id, username),
            self.show_profile_response)
    
    def report_spam(self, account_id, username):
        cmd = "lock_profile('%s');" % (i18n.get('reporting_as_spam'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.report_spam, (account_id, username), 
            self.report_spam_response)
    
    def block(self, account_id, username):
        cmd = "lock_profile('%s');" % (i18n.get('blocking_user'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.block, (account_id, username), 
            self.block_response)
    
    def follow(self, account_id, username):
        cmd = "lock_profile('%s');" % (i18n.get('following_user'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.follow, (account_id, username), 
            self.follow_response, True)
    
    def unfollow(self, account_id, username):
        cmd = "lock_profile('%s');" % (i18n.get('unfollowing_user'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.follow, (account_id, username), 
            self.follow_response, False)
    
    def mute(self, username):
        cmd = "lock_profile('%s');" % (i18n.get('muting_user'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.mute, (username), 
            self.mute_response, True)
    
    def unmute(self, username):
        cmd = "lock_profile('%s');" % (i18n.get('unmuting_user'))
        self.container.execute(cmd)
        
        self.worker.register(self.core.unmute, (username), 
            self.mute_response, False)
    
    def load_friends(self):
        self.worker.register(self.core.get_all_friends_list, None,
            self.load_friends_response)

    def showreply(self, account_id, status_id, status_id_replyto):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('loading'))
        self.container.execute(cmd)
        self.worker.register(self.core.get_single_status, (account_id, status_id_replyto), 
            self.showreply_response, status_id)

    def showconversation(self, account_id, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('loading'))
        self.container.execute(cmd)
        self.worker.register(self.core.get_conversation, (account_id, status_id), 
            self.showconversation_response, status_id)
    
    def short_urls(self, text):
        message = base64.b64decode(text)
        self.worker.register(self.core.autoshort_url, (message), 
            self.short_url_response)
    
    def direct_message(self, account, user, text):
        message = base64.b64decode(text)
        self.worker.register(self.core.send_direct, (account, user, message),
            self.direct_message_response)
    
    def profile_image(self, account, user):
        self.worker.register(self.core.get_profile_image, (account, user),
            self.profile_image_response)
    
    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------
    
    def update_status_response(self, response, account_id):
        if response.code > 0:
            self.container.execute('update_status_error("' + response.errmsg + '");')
        else:
            html_status = self.htmlparser.single_status(response.items)
            id_ = '#list-%s-timeline' % account_id
            self.container.prepend_element(id_, html_status, 'done_update_box(true);')
            column_key = '%s-timeline' % account_id
            if self.columns.has_key(column_key):
                self.columns[column_key].append(response.items)
        
    def broadcast_status_response(self, responses):
        cmd = ''
        bad_acc = []
        good_acc = []
        error = False
        for resp in responses:
            if resp.code > 0:
                error = True
                pr_name = i18n.get(resp.account_id.split('-')[1])
                bad_acc.append("%s (%s)" % (resp.account_id.split('-')[0], pr_name))
            else:
                html_status = self.htmlparser.status(resp.items)
                html_status = html_status.replace('"', '\\"')
                cmd += 'append_status_to_timeline("%s", "%s");' % (resp.account_id, html_status)
                good_acc.append(resp.account_id)
        
        if error:
            errmsg = i18n.get('error_posting_to') % (', '.join(bad_acc))
            accounts = '["' + '","'.join(good_acc) + '"]'
            cmd += 'broadcast_status_error(' + accounts + ', "' + errmsg + '");'
        else:
            cmd += 'done_update_box();'
        self.container.execute(cmd)
    
    def repeat_response(self, response, user_data):
        cmd = ''
        if response.code > 0:
            cmd = "show_notice('%s', 'error');" % response.errmsg
            current_status_id = user_data[1]
        else:
            status = response.items
            args = ARG_SEP.join([status.account_id, status.id_])
            if user_data[0]:
                newcmd = "cmd:unrepeat_status:%s" % args
                cmd = "update_retweeted_mark('%s', '%s', '%s', true); show_notice('%s', '%s');" % (status.id_, 
                    newcmd, i18n.get('-retweet'), i18n.get('successfully_retweeted'), 'info')
            else:
                newcmd = "cmd:repeat_status:%s" % args
                cmd = "update_retweeted_mark('%s', '%s', '%s', false); show_notice('%s', '%s');" % (status.id_, 
                    newcmd, i18n.get('+retweet'), i18n.get('retweet_successfully_undone'), 'info')
            current_status_id = status.id_
        cmd += "unlock_status('%s');" % (current_status_id)
        self.container.execute(cmd)
    
    def fav_response(self, response, fav=False):
        cmd = ''
        if response.code > 0:
            cmd = "show_notice('%s', 'error');" % response.errmsg
        else:
            status = response.items
            args = ARG_SEP.join([status.account_id, status.id_])
            if fav:
                newcmd = "cmd:unfav_status:%s" % args
                cmd = "update_favorite_mark('%s', '%s', '%s', true);" % (status.id_, 
                    newcmd, i18n.get('-fav'))
            else:
                newcmd = "cmd:fav_status:%s" % args
                cmd = "update_favorite_mark('%s', '%s', '%s', false);" % (status.id_, 
                    newcmd, i18n.get('+fav'))
        cmd += "unlock_status('%s');" % (status.id_)
        self.container.execute(cmd)
    
    def delete_status_response(self, response):
        cmd = ''
        if response.code > 0:
            cmd = "show_notice('%s', 'error');" % response.errmsg
        else:
            status = response.items
            cmd = "delete_status('%s'); show_notice('%s', '%s');" % (status.id_,
                i18n.get('successfully_deleted'), 'info')
        
        cmd += "unlock_status('%s');" % (status.id_)
        self.container.execute(cmd)
    
    def show_profile_response(self, response):
        cmd = ''
        if response.code > 0:
            cmd = 'profile_window_error("%s");' % response.errmsg
        else:
            profile = self.htmlparser.profile(response.items)
            profile = profile.replace('"', '\\"')
            cmd = 'update_profile_window("%s");' % (profile)
        self.container.execute(cmd)
    
    def report_spam_response(self, response):
        cmd = ''
        if response.code > 0:
            cmd = "unlock_profile(); show_notice('%s', '%s');" % (
                response.errmsg, 'error')
        else:
            cmd = "unlock_profile(); show_notice('%s', '%s');" % (
                i18n.get('user_reported_spam_successfully'), 'info')
        self.container.execute(cmd)
    
    def block_response(self, response):
        cmd = ''
        if response.code > 0:
            cmd = "unlock_profile(); show_notice('%s', '%s');" % (
                response.errmsg, 'error')
        else:
            cmd = "unlock_profile(); show_notice('%s', '%s');" % (
                i18n.get('user_blocked_successfully'), 'info')
        self.container.execute(cmd)
    
    def follow_response(self, response, follow=False):
        cmd = ''
        if response.code > 0:
            cmd = "show_notice('%s', 'error');" % response.errmsg
        else:
            profile = response.items
            cmd = ARG_SEP.join([profile.account_id, profile.username])
            if follow:
                newcmd = "cmd:unfollow:%s" % cmd
                message = i18n.get('you_are_now_following') % profile.username
                cmd = "update_profile_follow_cmd('%s', '%s'); show_notice('%s', '%s');" % (
                    newcmd, i18n.get('unfollow'), message, 'info')
            else:
                newcmd = "cmd:follow:%s" % cmd
                message = i18n.get('you_are_no_longer_following') % profile.username
                cmd = "update_profile_follow_cmd('%s', '%s'); show_notice('%s', '%s');" % (
                    newcmd, i18n.get('follow'), message, 'info')
        
        cmd += "unlock_profile();"
        self.container.execute(cmd)
    
    def mute_response(self, response, mute=False):
        cmd = ''
        if response.code > 0:
            cmd = "show_notice('%s', 'error');" % response.errmsg
        else:
            username = response.items
            if mute:
                newcmd = "cmd:unmute:%s" % username
                message = i18n.get('user_muted_successfully')
                cmd = "update_profile_mute_cmd('%s', '%s');" % (newcmd, i18n.get('unmute'))
                cmd += "show_notice('%s', '%s');" % (message, 'info')
                cmd += "mute_user('%s', true);" % username
            else:
                newcmd = "cmd:mute:%s" % username
                message = i18n.get('user_unmuted_successfully')
                cmd = "update_profile_mute_cmd('%s', '%s'); show_notice('%s', '%s');" % (
                    newcmd, i18n.get('mute'), message, 'info')
                cmd += "mute_user('%s', false);" % username
        cmd += "unlock_profile();"
        self.container.execute(cmd)
    
    def load_friends_response(self, response):
        cmd = ''
        if response.code > 0:
            cmd = "show_notice('%s', 'error'); unlock_autocomplete();" % response.errmsg
        else:
            users = []
            for profile in response:
                users.append(profile.username)
            friends = self.htmlparser.js_string_array(users)
            cmd = "show_notice('%s', 'info'); update_friends(%s);" % (
                i18n.get('friends_loaded_successfully'), friends)
        self.container.execute(cmd)
    
    def showconversation_response(self, response, status_id):
        statuses = response.items
        statuses.reverse()
        id_ = '#replystatus-%s' % status_id
        html_status = ''
        for status in statuses:
            if status.id_ != status_id:
                html_status += self.htmlparser.status(status, True)
        cmd = "unlock_status('%s');" % (status_id)
        cmd += "show_replies_to_status('%s')" % status_id
        self.container.update_element(id_, html_status, cmd)
    
    def showreply_response(self, response, status_id):
        status = response.items
        id_ = '#replystatus-%s' % status_id
        html_status = self.htmlparser.status(status, True)
        cmd = "unlock_status('%s');" % (status_id)
        cmd += "show_replies_to_status('%s')" % status_id
        self.container.update_element(id_, html_status, cmd)
    
    def short_url_response(self, response):
        cmd = ''
        if response.code > 0:
            cmd = 'update_status_error("' + response.errmsg + '");'
        else:
            cmd = 'set_update_box_message("' + response.items + '");'
        self.container.execute(cmd)
    
    def direct_message_response(self, response):
        if response.code > 0:
            self.container.execute('update_status_error("' + response.errmsg + '");')
        else:
            cmd = "show_notice('%s', 'info'); done_update_box_with_direct();" % (
                i18n.get('direct_message_sent_successfully'))
            self.container.execute(cmd)
    
    def profile_image_response(self, response):
        if response.code > 0:
            self.container.execute('hide_imageview(); show_notice("' + response.errmsg + '", "error");')
        else:
            img_url = 'file://' + response.items
            cmd = "update_imageview('%s');" % (img_url)
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
            self.columns[column.id_] = None
        
        self.container.execute("start_updating_column('" + column.id_ + "');")
        self.worker.register(self.core.get_column_statuses, (column.account_id, 
            column.column_name, 100), self.update_column, (column, notif))
        return True
        
    def refresh_column(self, column_id):
        for col in self.get_registered_columns():
            if col.build_id() == column_id:
                self.download_stream(col)
        
    def update_column(self, arg, data):
        column, notif = data
        self.log.debug('Updated column %s' % column.id_)
        
        if arg.code > 0:
            self.container.execute("stop_updating_column('" + column.id_ + "');")
            self.show_notice(arg.errmsg, 'error')
            return
        new_statuses = self.get_new_statuses(self.columns[column.id_], arg.items)
        
        if new_statuses == None:
            self.container.execute("stop_updating_column('" + column.id_ + "');")
            return

        page = self.htmlparser.statuses(new_statuses)
        element = "#list-%s" % column.id_
        extra = "stop_updating_column('" + column.id_ + "');"
        self.container.prepend_element(element, page, extra)
        
        # Notifications         
        count = len(new_statuses)
        if count != 0:
            if notif and self.core.show_notifications_in_updates():
                self.notify.updates(column, count)
            if self.core.play_sounds_in_notification():
                self.sound.updates()

        if not self.columns[column.id_]:
            self.columns[column.id_] = new_statuses
        else:
            self.columns[column.id_].extend(new_statuses)
        self.updating[column.id_] = False
        

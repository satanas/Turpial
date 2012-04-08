# -*- coding: utf-8 -*-

# PyQT main view for Turpial
#
# Author:  Carlos Guerrero (aka guerrerocarlos)
# Started: Sep 11, 2011

import os
from PyQt4 import QtCore, QtGui
from PyQt4.QtWebKit import *
import sys
import Queue
import logging
import threading

from turpial.ui.lang import i18n
from turpial.ui.html import HtmlParser
#from turpial.ui.gtk.about import About
from turpial.ui.qt.htmlview import HtmlView
from turpial.ui.qt.accounts import Accounts 
#from turpial.ui.gtk.dialogs.credentials import CredentialsDialog

#gtk.gdk.set_program_class("Turpial")
#gtk.gdk.threads_init()

log = logging.getLogger('Qt')

class Main(QtGui.QMainWindow):

    def changeLocation(self):
        url = QtCore.QUrl.fromUserInput(self.locationEdit.text())
        self.webView.load(url)
        self.webView.setFocus()
 

    def __init__(self, core):
        
        import sys
        self.app = QtGui.QApplication(sys.argv)
        super(Main, self).__init__()
        self.core = core

        self.htmlparser = HtmlParser()
        self.resize(310, 480)
        self.setWindowTitle("Turpial")
        self.container = HtmlView(self)


        self.setCentralWidget(self.container)
#        self.container.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
#        self.container.page().linkClicked.connect(self.__link_request)
#        self.container.page().linkClicked.connect(self.__link_request)


        self.mode = 0
        
        # Configuration
        self.showed = True
        self.minimize = 'on'
        self.version = '2.x'

        self.worker = Worker()
        #self.worker.start()
        self.accounts = Accounts(self)

        self.show()
        
    def main_loop(self):
        self.app.exec_()
    
    def show_main(self):
        page = self.htmlparser.main([], []) #['satanas82-twitter-timeline', 'satanas-identica-timeline'])
        self.container.render(page)

    def __action_request(self, url):
        url = str(url)
        
        action = url.split(':')[1]
        try:
            args = url.split(':')[1].split('-%&%-')
        except IndexError:
            args = []
        print url

        print "action: ",action
        
        if action == '//about':
            self.show_about()
        elif action == '//settings':
            self.container.execute("alert('hola');")
        elif action == '//accounts':
            self.accounts.show_all(self.core.all_accounts())
        elif action == '//login':
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
    
    def __link_request(self, url):
        print 'requested link: %s' % url
        self.__action_request(url.toString())
        
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
        
    def __close(self, event=None):
        if self.minimize == 'on':
            self.showed = False
            self.hide()
        else:
            self.main_quit()
            sys.exit(0)
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
        
    def main_loop_prev(self):
        try:
            gtk.gdk.threads_enter()
            gtk.main()
            gtk.gdk.threads_leave()
        except Exception:
            sys.exit(0)
    
    def show_login(self):
        page = self.htmlparser.login(self.core.all_accounts())
        self.container.render(page)
        
    def show_about(self):
        about = About(self)

    def show_preferences(self):
        pref = Preferences(self)

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
        if username == "" or username == None:
            username = "%s" % len(self.core.all_accounts());
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
            self.fav_response, (True, status_id))

    def unfav_status(self, account_id, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('removing_from_fav'))
        self.container.execute(cmd)

        self.worker.register(self.core.unmark_favorite, (account_id, status_id),
            self.fav_response, (False, status_id))

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
            self.delete_status_response, status_id)

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

    def show_reply(self, account_id, status_id, status_id_replyto):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('loading'))
        self.container.execute(cmd)
        self.worker.register(self.core.get_single_status, (account_id, status_id_replyto),
            self.show_reply_response, status_id)

    def show_conversation(self, account_id, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('loading'))
        self.container.execute(cmd)
        self.worker.register(self.core.get_conversation, (account_id, status_id),
            self.show_conversation_response, status_id)

    def hide_conversation(self, status_id):
        del self.openstatuses[status_id]
        cmd = "hide_replies_to_status('%s')" % status_id
        self.container.execute(cmd)

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

    def show_media(self, url, account_id): 
        cmd = "show_imageview();"
        self.container.execute(cmd)
        self.worker.register(self.core.get_media_content, (url, account_id),
            self.show_media_response)

    def delete_direct(self, account, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('deleting'))
        self.container.execute(cmd)

        self.worker.register(self.core.destroy_direct, (account, status_id),
            self.delete_status_response, status_id)

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
            #if self.columns.has_key(column_key):
            #    self.columns[column_key].append(response.items)

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
                column_key = '%s-timeline' % resp.account_id
                #if self.columns.has_key(column_key):
                #    self.columns[column_key].append(resp.items)

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

    def fav_response(self, response, user_data):
        fav = user_data[0]
        status_id = user_data[1]
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
        cmd += "unlock_status('%s');" % (status_id)
        self.container.execute(cmd)

    def delete_status_response(self, response, status_id):
        cmd = ''
        if response.code > 0:
            cmd = "show_notice('%s', 'error');" % response.errmsg
        else:
            status = response.items
            cmd = "delete_status('%s'); show_notice('%s', '%s');" % (status.id_,
                i18n.get('successfully_deleted'), 'info')

        cmd += "unlock_status('%s');" % (status_id)
        self.container.execute(cmd)

    def show_profile_response(self, response):
        cmd = ''
        if response.code > 0:
            cmd = 'profile_window_error("%s");' % response.errmsg
        else:
            profile = self.htmlparser.profile(response.items)
            profile = profile.replace('"', '\\"')
            profile = profile.replace('\r\n', '')
            profile = profile.replace('\n', '')
            cmd = 'update_profile_window2("%s");' % (profile)
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

    def show_conversation_response(self, response, status_id):
        statuses = response.items
        statuses.reverse()
        id_ = '#replystatus-%s' % status_id
        html_status = ''
        for status in statuses:
            if status.id_ != status_id:
                html_status += self.htmlparser.status(status, True)
                try:
                    self.openstatuses[status_id].append(status)
                except KeyError:
                    self.openstatuses[status_id] = []
                    self.openstatuses[status_id].append(status)
        cmd = "unlock_status('%s');" % (status_id)
        cmd += "show_replies_to_status('%s', true)" % status_id
        self.container.update_element(id_, html_status, cmd)

    def show_reply_response(self, response, status_id):
        status = response.items
        id_ = '#replystatus-%s' % status_id
        html_status = self.htmlparser.status(status, True)
        cmd = "unlock_status('%s');" % (status_id)
        cmd += "show_replies_to_status('%s', true)" % status_id
        self.container.update_element(id_, html_status, cmd)

    def short_url_response(self, response):
        cmd = ''
        if response.code > 0:
            cmd = 'update_status_error("' + response.errmsg + '");'
        else:
            new_msg = response.items.replace('"', '\\"')
            cmd = 'set_update_box_message("' + new_msg + '");'
            print cmd
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
            self.columns[column.id_] = None

        num_statuses = self.core.get_max_statuses_per_column()
        self.container.execute("start_updating_column('" + column.id_ + "');")
        self.worker.register(self.core.get_column_statuses, (column.account_id,
            column.column_name, num_statuses), self.update_column, 
            (column, notif, num_statuses))
        return True

    def refresh_column(self, column_id):
        for col in self.get_registered_columns():
            if col.build_id() == column_id:
                self.download_stream(col)

    def update_column(self, arg, data):
        column, notif, max_ = data
        self.log.debug('Updated column %s' % column.id_)

        if arg.code > 0:
            self.container.execute("stop_updating_column('" + column.id_ + "');")
            self.show_notice(arg.errmsg, 'error')
            return
        page = self.htmlparser.statuses(arg.items)
        element = "#list-%s" % column.id_
        extra = "stop_updating_column('" + column.id_ + "');"
        self.container.update_element(element, page, extra)

        # Notifications
        # FIX: Do not store an array with statuses objects, find a way to store
        # maybe just ids
        count = self.get_new_statuses(self.columns[column.id_], arg.items)
        if count != 0:
            if notif and self.core.show_notifications_in_updates():
                self.notify.updates(column, count)
            if self.core.play_sounds_in_notification():
                self.sound.updates()
            if not self.is_active():
                self.set_urgency_hint(True)
                self.unitylauncher.increment_count(count)
                self.unitylauncher.set_count_visible(True)
            else:
                self.unitylauncher.set_count_visible(False)
        self.columns[column.id_] = arg.items
        self.updating[column.id_] = False

        self.restore_open_tweets()

    def restore_open_tweets(self):
        for status in self.openstatuses:
            html_status = ''
            id_ = '#replystatus-%s' % status
            for rep_status in self.openstatuses[status]:
                html_status += self.htmlparser.status(rep_status, True)
            cmd = "show_replies_to_status('%s', false)" % status
            self.container.update_element(id_, html_status, cmd)

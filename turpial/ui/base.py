# -*- coding: utf-8 -*-

# Base class for all the Turpial interfaces
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import os
import sys
import base64
import urllib
import logging
import webbrowser
import subprocess

from xml.sax.saxutils import unescape

from libturpial.common import *
from libturpial.api.models.mediacontent import *
from libturpial.api.interfaces.service import ServiceResponse
from libturpial.api.services.showmedia import utils as showmediautils

from turpial import VERSION
from turpial.ui.lang import i18n
from turpial.singleton import Singleton
from turpial.ui.unity.unitylauncher import UnityLauncherFactory

MIN_WINDOW_WIDTH = 250

class Base(Singleton):
    ACTION_REPEAT = 'repeat'
    ACTION_UNREPEAT = 'unrepeat'
    ACTION_FAVORITE = 'favorite'
    ACTION_UNFAVORITE = 'unfavorite'

    '''Parent class for every UI interface'''
    def __init__(self, core):
        Singleton.__init__(self, 'turpial.pid')
        self.core = core
        self.log = logging.getLogger('UI')
        self.log.debug('Started')

        self.images_path = os.path.realpath(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'pixmaps'))


        # Unity integration
        self.unitylauncher = UnityLauncherFactory().create();
        #self.unitylauncher.add_quicklist_button(self.show_update_box, i18n.get('new_tweet'), True)
        #self.unitylauncher.add_quicklist_checkbox(self.sound.disable, i18n.get('enable_sounds'), True, not self.sound._disable)
        #self.unitylauncher.add_quicklist_button(self.show_update_box_for_direct, i18n.get('direct_message'), True)
        #self.unitylauncher.add_quicklist_button(self.show_accounts_dialog, i18n.get('accounts'), True)
        #self.unitylauncher.add_quicklist_button(self.show_preferences, i18n.get('preferences'), True)
        #self.unitylauncher.add_quicklist_button(self.main_quit, i18n.get('exit'), True)
        #self.unitylauncher.show_menu()

    # TODO: Put this in util.py
    def humanize_size(self, size):
        if size == 0:
            return '0 B'

        kbsize = size / 1024
        if kbsize > 0:
            mbsize = kbsize / 1024
            if mbsize > 0:
                gbsize = mbsize / 1024
                if gbsize > 0:
                    return "%.2f GB" % (mbsize / 1024.0)
                else:
                    return "%.2f MB" % (kbsize / 1024.0)
            else:
                return "%.2f KB" % (size / 1024.0)
        else:
            return "%.2f B" % size

    #================================================================
    # Common methods to all interfaces
    #================================================================

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

    def get_max_statuses_per_column(self):
        return self.core.get_max_statuses_per_column()

    def disable_sound(self, widget=None):
        self.sound.disable(not widget.get_active())

    def get_color_scheme(self, key):
        color = {
            'links': '#ff6633',
        }
        return color[key]

    def save_account(self, username, protocol_id, password):
        if username == "" or username == None:
            username = "%s" % len(self.core.all_accounts())
        account_id = self.core.register_account(username, protocol_id, password)
        self.after_save_account(account_id)

    def delete_account(self, account_id):
        # FIXME: Implement try/except
        for col in self.get_registered_columns():
            if col.account_id == account_id:
                self.delete_column(col.id_)
        self.core.unregister_account(account_id, True)
        self.after_delete_account(True)

    def save_column(self, column_id):
        column = self.core.register_column(column_id)
        self.after_save_column(column)

    def delete_column(self, column_id):
        self.core.unregister_column(column_id)
        if self.columns.has_key(column_id):
            del self.columns[column_id]
        self.after_delete_column(column_id)

    def start(self):
        #if self.core.play_sounds_in_login():
        #    self.sound.login()

        for account_id in self.get_accounts_list():
            self.core.change_login_status(account_id, LoginStatus.IN_PROGRESS)
            self.login(account_id)

        self.after_login()

    def open_url(self, url):
        browser = self.core.get_default_browser()

        if showmediautils.is_service_supported(url):
            self.show_media(url)
        elif browser != '':
            cmd = browser.split(' ')
            cmd.append(url)
            self.log.debug('Opening URL %s with %s' % (url, browser))
            subprocess.Popen(cmd)
        else:
            self.log.debug('Opening URL %s with default browser' % url)
            webbrowser.open(url)

    def update_status(self, accounts, message, in_reply_to=None):
        if len(accounts) > 1:
            self.worker.register(self.core.broadcast_status, (accounts, message),
                self.after_broadcast_status)
        else:
            self.worker.register(self.core.update_status, (accounts[0],
                message, in_reply_to), self.after_update_status, accounts[0])

    def direct_message(self, account, user, message):
        self.worker.register(self.core.send_direct, (account, user, message),
            self.after_direct_message)

    def repeat_status(self, status):
        self.worker.register(self.core.repeat_status, (status.account_id, status.id_),
            self.after_repeat, (self.ACTION_REPEAT))

    def unrepeat_status(self, status):
        self.worker.register(self.core.unrepeat_status, (status.account_id, status.id_),
            self.after_repeat, (self.ACTION_UNREPEAT))

    def favorite_status(self, status):
        self.worker.register(self.core.mark_favorite, (status.account_id, status.id_),
            self.after_favorite, (self.ACTION_FAVORITE))

    def unfavorite_status(self, status):
        self.worker.register(self.core.unmark_favorite, (status.account_id, status.id_),
            self.after_favorite, (self.ACTION_UNFAVORITE))

    def delete_status(self, status):
        self.worker.register(self.core.destroy_status, (status.account_id, status.id_),
            self.after_delete_status)

    def autoshort_url(self, message):
        self.worker.register(self.core.autoshort_url, (message),
            self.after_autoshort_url)

    #================================================================
    # Hooks that can be implemented on each interface (optionals)
    #================================================================

    def after_save_account(self, account_id, err_msg=None):
        pass

    def after_delete_account(self, deleted, err_msg=None):
        pass

    def after_save_column(self, column_id, err_msg=None):
        pass

    def after_delete_column(self, column_id, err_msg=None):
        pass

    def after_login(self):
        pass

    def after_update_status(self, response, account_id):
        pass

    def after_broadcast_status(self, response):
        pass

    def after_direct_message(self, response):
        pass

    def after_repeat(self, response, action):
        """ Method used for repeat and unrepeat statuses """
        pass

    def after_favorite(self, response, action):
        """ Method used for favorite and unfavorite statuses """
        pass

    def after_delete_status(self, response):
        pass

    def after_autoshort_url(self, response):
        pass

    #================================================================
    # Methods to override
    #================================================================

    def main_loop(self):
        raise NotImplementedError

    def main_quit(self, widget=None, force=False):
        raise NotImplementedError

    def show_main(self):
        raise NotImplementedError

    def show_notice(self, message, type_):
        raise NotImplementedError

    def show_media(self, url):
        raise NotImplementedError

    def login(self, account):
        raise NotImplementedError


    '''

    def on_link_request(self, url):
        self.open_url(url)

    def on_action_request(self, url):
        action, args = self.htmlparser.parse_command(url)
        print action, args
        if action == 'about':
            self.show_about()
        elif action == 'preferences':
            self.show_preferences()
        elif action == 'accounts_manager':
            self.accountsdlg.show()
        elif action == 'columns_menu':
            self.show_column_menu()
        elif action == 'profiles_menu':
            self.show_profile_menu()
        elif action == 'repeat_menu':
            self.show_repeat_menu(args)
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
        elif action == 'show_conversation':
            self.show_conversation(args[0], args[1])
        elif action == 'hide_conversation':
            self.hide_conversation(args[0])
        elif action == 'short_urls':
            self.short_urls(args[0])
        elif action == 'direct_message':
            self.direct_message(args[0], args[1], args[2])
        elif action == 'profile_image':
            self.profile_image(args[0], args[1])
        elif action == 'show_media':
            self.show_media(args[0].replace("$", ":"), args[1])
        elif action == 'delete_direct':
            self.delete_direct(args[0], args[1])
        elif action == 'turpial_all':
            self.get_turpial_all()

    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------

    def _login_callback(self, arg, account_id):
        pass


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
            tmp_cmd = "<a name='fav-cmd' href='%s' class='action'>%s</a>"
            if fav:
                fav_cmd = "cmd:unfav_status:%s" % args
                full_cmd = tmp_cmd % (fav_cmd, self.__image_tag('action-fav.png', tooltip=i18n.get('-fav')))
                cmd = "update_favorite_mark('%s', '%s', true);" % (status.id_, full_cmd)
            else:
                fav_cmd = "cmd:fav_status:%s" % args
                full_cmd = tmp_cmd % (fav_cmd, self.__image_tag('action-unfav.png', tooltip=i18n.get('+fav')))
                cmd = "update_favorite_mark('%s', '%s', false);" % (status.id_, full_cmd)
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

    def load_all_friends_response(self, users):
        friends = self.htmlparser.js_string_array(users)
        cmd = "update_friends(%s);" % friends
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

    #---------------------------------------------------------------------------

    def reply_status(self, account, status_id, text):
        message = base64.b64decode(text)
        self.worker.register(self.core.update_status, (account, message, status_id),
            self.update_status_response, account)

    def show_profile(self, account_id, username):
        #self.container.execute('show_profile_modal()')
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

        self.worker.register(self.core.unfollow, (account_id, username),
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

    def profile_image(self, account, user):
        self.imageview.loading()
        self.worker.register(self.core.get_profile_image, (account, user),
            self.profile_image_response)

    def show_media(self, url, account_id): 
        self.imageview.loading()
        self.worker.register(self.core.get_media_content, (url, account_id),
            self.show_media_response)

    def delete_direct(self, account, status_id):
        cmd = "lock_status('%s', '%s');" % (status_id, i18n.get('deleting'))
        self.container.execute(cmd)

        self.worker.register(self.core.destroy_direct, (account, status_id),
            self.delete_status_response, status_id)


    def restore_open_tweets(self):
        for status in self.openstatuses:
            html_status = ''
            id_ = '#replystatus-%s' % status
            for rep_status in self.openstatuses[status]:
                html_status += self.htmlparser.status(rep_status, True)
            cmd = "show_replies_to_status('%s', false)" % status
            self.container.update_element(id_, html_status, cmd)
    '''
 

    def get_new_statuses(self, current, last):
        if not current:
            return len(last)
        if not last:
            return 0

        count = 0
        our_last_status_id = current[0].id_

        for last_status in last:
            if last_status.id_ != our_last_status_id:
                count +=1
            else:
                break

        return count

    def save_window_geometry(self, width, height):
        pass

    def get_config(self):
        return self.core.get_config()

    def save_config(self, new_config):
        self.core.save_all_config(new_config)

    def get_filters(self):
        return self.core.list_filters()

    def save_filters(self, lst):
        self.core.save_filters(lst)

    def restore_default_config(self):
        self.core.delete_current_config()

    def delete_all_cache(self):
        self.core.delete_cache()

    def get_cache_size(self):
        return self.humanize_size(self.core.get_cache_size())

    def get_turpial_all(self):
        cmd = "show_imageview();"
        self.container.execute(cmd)
        chunk = '\x89PNG'
        filepath = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', 'data', 'pixmaps', 'turpial-all.dat'))
        fd = open(filepath, 'r')
        rawimg = chunk + fd.read()
        fd.close()
        resp = ServiceResponse(MediaContent(IMAGE_CONTENT, 'all.png', rawimg))
        return self.show_media_response(resp)


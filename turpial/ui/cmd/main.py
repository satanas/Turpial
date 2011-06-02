# -*- coding: utf-8 -*-

# Vista para Turpial en PyGTK
#
# Author: Wil Alvarez (aka Satanas)
# Nov 08, 2009

import os
import base64
import logging

from turpial.ui.base_ui import BaseGui
from turpial.notification import Notification
from turpial.ui import util as util
from turpial.sound import Sound
from turpial.config import PROTOCOLS

log = logging.getLogger('Cmd')


class Main(BaseGui):
    def __init__(self, controller, cmdline):
        BaseGui.__init__(self, controller)
        self.cmdline = cmdline
        self.controller = controller
    
    def __usage(self):
        print "Usage: turpial -i cmd <COMMAND> <PROTOCOL> [ARGS]"
        print "    COMMAND: desired command"
        print "    PROTOCOL: number of desired protocol to perform action"
        print "    ARGS: arguments needed for each command"
        print
        
    def __print_try_ls(self):
        print "Try 'turpial -i cmd ls' for a list of available commands"
        
    def __print_try_lsp(self):
        print "Try 'turpial -i cmd lsp' for a list of available protocols"
        
    def __command_list(self):
        print "COMMANDS:"
        print "  ls"
        print "    Show this list"
        print "  lsp"
        print "    List all available protocols"
        print "  update [MESSAGE]"
        print "    Post an update on the current account/protocol"
        
    def __protocol_list(self):
        print "PROTOCOLS:"
        for i in range(len(PROTOCOLS)):
            print "[%d] - %s" % (i, PROTOCOLS[i])
    
    def quit(self, arg=None):
        self.request_signout()
        
    def main_loop(self):
        if len(self.cmdline) < 1:
            print "Missing operands"
            self.__usage()
            self.__print_try_ls()
            self.quit()
            return
        
        cmd = self.cmdline[0]
        
        if len(self.cmdline) == 1:
            self.__process_without_args(cmd)
        elif len(self.cmdline) > 1:
            try:
                protocol = int(self.cmdline[1])
            except ValueError:
                print "ERROR: Specify a valid protocol"
                self.__usage()
                self.__print_try_lsp()
                self.quit()
                return
            args = self.cmdline[2:]
            self.__process_with_args(cmd, protocol, args)
    
    def __process_without_args(self, cmd):
        self.__usage()
        if cmd == 'help':
            self.__print_try_ls()
        elif cmd == 'ls':
            self.__command_list()
        elif cmd == 'lsp':
            self.__protocol_list()
        self.quit()
    
    def __process_with_args(self, cmd, protocol, args):
        user, passwd, rem = self.controller.get_remembered(protocol)
        info_str = "in %s as %s" % (PROTOCOLS[protocol], user)
        
        if user == '' or passwd == '':
            print "You need to configurate an account in order to use this interface."
            print "Execute 'turpial --save-credentials' to configurate an account"
            self.quit()
            return
        
        if cmd == 'update':
            if len(args) < 1:
                print "ERROR: You need to specify a message to post"
                return
            message = args[0]
            print "Posting message", info_str
            self.controller.signin(user, passwd, PROTOCOLS[protocol])
            self.controller.update_status(message)

    def tweet_done(self, tweets):
        if tweets.type == 'status':
            print "Mensaje enviado con éxito"
        else:
            print tweets.errmsg
        self.quit()
    
    def show_login(self):
        pass
    
    def resize_avatar(self, pic):
        pass
        
    def show_main(self, config, global_config,  profile):
        pass
        
    def set_lists(self, lists, viewed):
        pass
        
    def show_oauth_pin_request(self, url):
        pass
        
    def cancel_login(self):
        pass
        
    def start_updating_column1(self):
        pass
        
    def start_updating_column2(self):
        pass
        
    def start_updating_column3(self):
        pass
        
    def start_search(self):
        pass
        
    def update_tweet(self, tweet):
        pass
        
    def update_column1(self, tweets):
        pass
        
    def update_column2(self, replies):
        pass
        
    def update_column3(self, directs):
        pass
        
    def update_favorites(self, favs):
        pass
        
    def update_rate_limits(self, rates):
        pass
        
    def update_follow(self, user, follow):
        pass
        
    def update_user_avatar(self, user, avatar):
        pass
        
    def update_user_profile(self, profile):
        pass
        
    def update_search(self, topics):
        pass
        
    def update_in_reply_to(self, tweets):
        pass
        
    def update_conversation(self, tweets):
        pass
        
    def tweet_changed(self, timeline, replies, favs):
        pass
        
    def update_config(self, config):
        pass
    
    def set_column_item(self, index, reset=False):
        pass

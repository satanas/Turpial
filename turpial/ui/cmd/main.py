# -*- coding: utf-8 -*-

"""Shell interface for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# 26 Jun, 2011

import cmd
import getpass
import logging

VERSION = '2.0'

INTRO = [
    'Welcome to Turpial (shell mode).', 
    'Type "help" to get a list of available commands.',
    'Type "help <command>" to get a detailed help about that command'
]

ARGUMENTS = {
    'account': ['add', 'edit', 'delete', 'list', 'change', 'default'],
    'status': ['update', 'reply', 'delete', 'conversation'],
    'profile': ['me', 'user', 'update'],
    'friend': ['list', 'follow', 'unfollow', 'block', 'unblock', 'spammer',
        'check'],
    'direct': ['send', 'delete'],
    'favorite': ['mark', 'unmark'],
}

class Main(cmd.Cmd):
    def __init__(self, core, config):
        cmd.Cmd.__init__(self)
        
        self.log = logging.getLogger('Turpial:CMD')
        self.prompt = 'turpial> '
        self.intro = '\n'.join(INTRO)
        self.core = core
        self.account = None
        
    def show_main(self):
        pass
        
    def main_loop(self):
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            self.do_exit()
        except EOFError:
            self.do_exit()
    
    def __validate_index(self, index, array, blank=False):
        try:
            a = array[int(index)]
            return True
        except IndexError:
            return False
        except ValueError:
            if blank and index == '':
                return True
            elif not blank and index == '':
                return False
            elif blank and index != '':
                return False
        except TypeError:
            if index is None:
                return False
    
    def __validate_accounts(self):
        if len(self.core.list_accounts()) > 0:
            return True
        print "You don't have any registered account. Run 'account add' command"
        return False
    
    def __validate_default_account(self):
        if self.account:
            return True
        print "You don't have a default account. Run 'account change' command"
        return False
        
    def __validate_arguments(self, arg_array, value):
        if value in arg_array:
            return True
        else:
            print 'Invalid Argument'
            return False
    
    def __build_message_menu(self):
        text = raw_input('Message: ')
        if text == '':
            print 'You must write something to post'
            return None
        
        if len(text) > 140:
            trunc = raw_input ('Your message has more than 140 characters. Do you want truncate it? [Y/n]: ')
            if trunc.lower() == 'y' or trunc == '':
                return text[:140]
            return None
        return text
    
    def __build_accounts_menu(self, _all=False):
        if len(self.core.list_accounts()) == 1: 
            return self.core.list_accounts()[0]
        
        index = None
        while 1:
            accounts = self.__show_accounts()
            if _all:
                index = raw_input('Select account (or Enter for all): ')
            else:
                index = raw_input('Select account: ')
            if not self.__validate_index(index, accounts, _all):
                print "Invalid account"
            else:
                break
        if index == '':
            return ''
        else:
            return accounts[int(index)]
    
    def __build_password_menu(self, account):
        passwd = None
        while 1:
            passwd = getpass.unix_getpass("Password for '%s' in '%s': " % (
                account.split('-')[0], account.split('-')[1]))
            if passwd:
                return passwd
            else:
                print "Password can't be blank"
            
    def __build_change_account_menu(self):
        if len(self.core.list_accounts()) == 1:
            if self.account:
                print "Your unique account is already your default"
            else:
                self.__add_first_account_as_default()
        elif len(self.core.list_accounts()) > 1:
            while 1:
                accounts = self.__show_accounts()
                index = raw_input('Select you new default account (or Enter for keep current): ')
                if index == '':
                    print "Default account remain with no changes"
                    return True
                if not self.__validate_index(index, accounts):
                    print "Invalid account"
                else:
                    break
            self.account = accounts[int(index)]
            print "Set %s in %s as your new default account" % (
                self.account.split('-')[0], self.account.split('-')[1])
        
    def __build_protocols_menu(self):
        index = None
        protocols = self.core.list_protocols()
        while 1:
            print "Available protocols:"
            for i in range(len(protocols)):
                print "[%i] %s" % (i, protocols[i])
            index = raw_input('Select protocol: ')
            if not self.__validate_index(index, protocols):
                print "Invalid protocol"
            else:
                break
        return protocols[int(index)]
    
    def __build_confirm_menu(self, message):
        confirm = raw_input(message + ' [y/N]: ')
        if confirm.lower() == 'y':
            return True
        else:
            return False
            
    def __user_input(self, message, blank=False):
        while 1:
            text = raw_input(message)
            if text == '' and not blank:
                print "You can't leave this field blank"
                continue
            break
        return text
        
    def __add_first_account_as_default(self):
        self.account = self.core.list_accounts()[0]
        print "Selected account %s in %s as default (*)" % (
            self.account.split('-')[0], self.account.split('-')[1])
    
    def __show_accounts(self):
        if len(self.core.list_accounts()) == 0:
            print "There are no registered accounts"
            return
        
        accounts = []
        print "Available accounts:"
        for acc in self.core.list_accounts():
            ch = ''
            if acc == self.account:
                ch = ' (*)'
            print "[%i] %s - %s%s" % (len(accounts), acc.split('-')[0], acc.split('-')[1], ch)
            accounts.append(acc)
        return accounts
        
    def __show_profiles(self, people):
        if not statuses:
            print "There are no profiles to show"
            return

        if people.code > 0: 
            print people.errmsg
            return
        
        for p in people:
            protected = '<protected>' if p.protected else ''
            following = '<following>' if p.following else ''
            
            header = "@%s (%s) %s %s" % (p.username, p.fullname, 
                following, protected)
            print header
            print '-' * len(header)
            print "URL: %s" % p.url
            print "Location: %s" % p.location
            print "Bio: %s" % p.bio
            if p.last_update: 
                print "Last: %s" % p.last_update
            print ''
    
    def __show_statuses(self, statuses):
        if not statuses:
            print "There are no statuses to show"
            return
        
        if statuses.code > 0:
            print statuses.errmsg
            return
        
        count = 1
        for status in statuses:
            text = status.text.replace('\n', ' ')
            inreply = ''
            client = ''
            if status.in_reply_to_user:
                inreply = ' in reply to %s' % status.in_reply_to_user
            if status.source:
                client = ' from %s' % status.source.name
            print "%d. @%s: %s (id: %s)" % (count, status.username, text, status.id_)
            print "%s%s%s" % (status.datetime, client, inreply)
            if status.reposted_by:
                users = ''
                for u in status.reposted_by:
                    users += u + ' '
                print 'Retweeted by %s' % status.reposted_by
            print
            count += 1
    
    def __process_login(self, acc):
        if not self.core.has_stored_passwd(acc):
            passwd = self.__build_password_menu(acc)
            username = acc.split('-')[0]
            protocol = acc.split('-')[1]
            self.core.register_account(username, protocol, passwd)
        
        rtn = self.core.login(acc)
        if rtn.code > 0:
            print rtn.errmsg
            return
        
        auth_obj = rtn.items
        if auth_obj.must_auth():
            print "Please visit %s, authorize Turpial and type the pin returned" % auth_obj.url
            pin = self.__user_input('Pin: ')
            self.core.authorize_oauth_token(acc, pin)
        
        rtn = self.core.auth(acc)
        if rtn.code > 0:
            print rtn.errmsg
        else:
            print 'Logged in with account %s' % acc.split('-')[0]
        
    def default(self, line):
        print '\n'.join(['Command not found.', INTRO[1], INTRO[2]])
        
    def emptyline(self):
        pass
    
    def do_account(self, arg):
        if not self.__validate_arguments(ARGUMENTS['account'], arg): 
            self.help_account(False)
            return False
        
        if arg == 'add':
            username = raw_input('Username: ')
            password = getpass.unix_getpass('Password: ')
            remember = self.__build_confirm_menu('Remember password')
            protocol = self.__build_protocols_menu()
            acc_id = self.core.register_account(username, protocol, password, remember)
            print 'Account added'
            if len(self.core.list_accounts()) == 1: 
                self.__add_first_account_as_default()
        elif arg == 'edit':
            if not self.__validate_default_account(): 
                return False
            password = getpass.unix_getpass('New Password: ')
            username = self.account.split('-')[0]
            protocol = self.account.split('-')[1]
            remember = self.__build_confirm_menu('Remember password')
            self.core.register_account(username, protocol, password, remember)
            print 'Account edited'
        elif arg == 'delete':
            if not self.__validate_accounts(): 
                return False
            account = self.__build_accounts_menu()
            conf = self.__build_confirm_menu('Do you want to delete account %s?' %
                account)
            if not conf:
                print 'Command cancelled'
                return False
            del_all = self.__build_confirm_menu('Do you want to delete all data?')
            self.core.unregister_account(account, del_all)
            if self.account == account:
                self.account = None
            print 'Account deleted'
        elif arg == 'change':
            if not self.__validate_accounts():
                return False
            self.__build_change_account_menu()
        elif arg == 'list':
            self.__show_accounts()
        elif arg == 'default':
            print "Your default account is %s in %s" % (
                self.account.split('-')[0], self.account.split('-')[1])
    
    def help_account(self, desc=True):
        text = 'Manage user accounts'
        if not desc:
            text = ''
        print '\n'.join([text,
            'Usage: account <arg>\n',
            'Possible arguments are:',
            '  add:\t\t Add a new user account',
            '  edit:\t\t Edit an existing user account',
            '  delete:\t Delete a user account',
            '  list:\t\t Show all registered accounts',
            '  default:\t Show default account',
        ])
    
    def do_login(self, arg):
        if not self.__validate_accounts(): 
            return False
        
        _all = True
        if len(self.core.list_accounts()) > 1:
            _all = self.__build_confirm_menu('Do you want to login with all available accounts?')
        
        if _all:
            work = False
            for acc in self.core.list_accounts():
                if self.core.is_account_logged_in(acc):
                    continue
                work = True
                self.__process_login(acc)
            if not work:
                print "Already logged in with all available accounts"
        else:
            acc = self.__build_accounts_menu()
            self.__process_login(acc)
    
    def help_login(self):
        print 'Login with one or many accounts'
    
    def do_profile(self, arg):
        if not self.__validate_arguments(ARGUMENTS['profile'], arg): 
            self.help_profile(False)
            return False
        
        if not self.__validate_default_account(): 
            return False
        
        if arg == 'me':
            profile = self.core.get_own_profile(self.account)
            if profile is None:
                print 'You must be logged in'
            else:
                self.__show_profiles(profile)
        elif arg == 'user':
            username = raw_input('Type the username: ')
            if username == '':
                print 'You must specify a username'
                return False
            profile = self.core.get_user_profile(self.account, username)
            if profile is None:
                print 'You must be logged in'
            else:
                self.__show_profiles(profile)
        elif arg == 'update':
            args = {}
            name = raw_input('Type your name (ENTER for none): ')
            bio = raw_input('Type your bio (ENTER for none): ')
            url = raw_input('Type your url (ENTER for none): ')
            location = raw_input('Type your location (ENTER for none): ')
            
            if name != '':
                args['name'] = name
            if bio != '':
                args['description'] = bio
            if url != '':
                args['url'] = url
            if location != '':
                args['location'] = location
            result = self.core.update_profile(self.account, args)
            
            if result.code > 0: 
                print result.errmsg
            else:
                print 'Profile updated'
    
    def help_profile(self, desc=True):
        text = 'Manage user profile'
        if not desc:
            text = ''
        print '\n'.join([text,
            'Usage: profile <arg>\n',
            'Possible arguments are:',
            '  me:\t\t Show own profile',
            '  user:\t\t Show profile for a specific user',
            '  update:\t Update own profile',
        ])
    
    def do_status(self, arg):
        if not self.__validate_default_account(): 
            return False
        
        if not self.__validate_arguments(ARGUMENTS['status'], arg): 
            self.help_status(False)
            return False
        
        if arg == 'update':
            message = self.__build_message_menu()
            if not message:
                print 'You must to write something'
                return False
            
            broadcast = self.__build_confirm_menu('Do you want to post the message in all available accounts?')
            if broadcast:
                for acc in self.core.list_accounts():
                    rtn = self.core.update_status(acc, message)
                    if rtn.code > 0:
                        print rtn.errmsg
                    else:
                        print 'Message posted in account %s' % acc.split('-')[0]
            else:
                rtn = self.core.update_status(self.account, message)
                if rtn.code > 0:
                    print rtn.errmsg
                else:
                    print 'Message posted in account %s' % self.account.split('-')[0]
        elif arg == 'reply':
            reply_id = raw_input('Status ID: ')
            if reply_id == '':
                print "You must specify a valid id"
                return False
            message = self.__build_message_menu()
            if not message:
                print 'You must to write something'
                return False
            rtn = self.core.update_status(self.account, message, reply_id)
            if rtn.code > 0:
                print rtn.errmsg
            else:
                print 'Reply posted in account %s' % self.account.split('-')[0]
        elif arg == 'delete':
            status_id = raw_input('Status ID: ')
            if status_id == '':
                print "You must specify a valid id"
                return False
            rtn = self.core.destroy_status(self.account, status_id)
            if rtn.code > 0:
                print rtn.errmsg
            else:
                print 'Status deleted'
        elif arg == 'conversation':
            status_id = raw_input('Status ID: ')
            if status_id == '':
                print "You must specify a valid id"
                return False
            rtn = self.core.get_conversation(self.account, status_id)
            if rtn.code > 0:
                print rtn.errmsg
            else:
                self.__show_statuses(rtn)
    
    def help_status(self, desc=True):
        text = 'Manage statuses for each protocol'
        if not desc:
            text = ''
        print '\n'.join([text,
           'Usage: status <arg>\n',
            'Possible arguments are:',
            '  update:\t Update status ',
            '  delete:\t Delete status',
            '  conversation:\t Show related tweets as conversation',
        ])
    
    def do_column(self, arg):
        if not self.__validate_default_account(): 
            return False
        
        lists = self.core.list_columns_per_account(self.account)
        if arg == '':
            self.help_column(False)
        elif arg == 'list':
            if len(lists) == 0:
                print "No column available. Maybe you need to login"
                return False
            print "Available columns:"
            for li in lists:
                print "  %s" % li
        elif arg == 'public':
            rtn = self.core.get_public_timeline(self.account)
            self.__show_statuses(rtn)
        else:
            if len(lists) == 0:
                print "No column available. Maybe you need to login"
                return False
            if arg in lists:
                rtn = self.core.get_column_statuses(self.account, arg)
                self.__show_statuses(rtn)
            else:
                print "Invalid column '%s'" % arg
    
    def help_column(self, desc=True):
        text = 'Show user columns'
        if not desc:
            text = ''
        print '\n'.join([text,
           'Usage: column <arg>\n',
            'Possible arguments are:',
            '  list:\t\t List all available columns for that account',
            '  timeline:\t Show timeline',
            '  replies:\t Show replies',
            '  directs:\t Show directs messages',
            '  favorites:\t Show statuses marked as favorites',
            '  public:\t Show public timeline',
            '  <list_id>:\t Show statuses for the user list with id <list_id>',
        ])
        
    def do_friend(self, arg):
        if not self.__validate_default_account(): 
            return False
        
        if not self.__validate_arguments(ARGUMENTS['friend'], arg): 
            self.help_friend(False)
            return False
        
        if arg == 'list':
            friends = self.core.get_friends(self.account)
            if friends.code > 0:
                print rtn.errmsg
                return False
            
            if len(friends) == 0:
                print "Hey! What's wrong with you? You've no friends"
                return False
            print "Friends list:"
            for fn in friends:
                print "+ @%s (%s)" % (fn.username, fn.fullname)
        elif arg == 'follow':
            username = raw_input('Username: ')
            if username == '':
                print "You must specify a valid user"
                return False
            rtn = self.core.follow(self.account, username)
            if rtn.code > 0:
                print rtn.errmsg
                return False
            print "Following %s" % user
        elif arg == 'unfollow':
            username = raw_input('Username: ')
            if username == '':
                print "You must specify a valid user"
                return False
            rtn = self.core.unfollow(self.account, username)
            if rtn.code > 0:
                print rtn.errmsg
                return False
            print "Not following %s" % user
        elif arg == 'block':
            username = raw_input('Username: ')
            if username == '':
                print "You must specify a valid user"
                return False
            rtn = self.core.block(self.account, username)
            if rtn.code > 0:
                print rtn.errmsg
                return False
            print "Blocking user %s" % username
        elif arg == 'unblock':
            username = raw_input('Username: ')
            if username == '':
                print "You must specify a valid user"
                return False
            rtn = self.core.unblock(self.account, username)
            if rtn.code > 0:
                print rtn.errmsg
                return False
            print "Unblocking user %s" % username
        elif arg == 'spammer':
            username = raw_input('Username: ')
            if username == '':
                print "You must specify a valid user"
                return False
            rtn = self.core.report_spam(self.account, username)
            if rtn.code > 0:
                print rtn.errmsg
                return False
            print "Reporting user %s as spammer" % username
        elif arg == 'check':
            username = raw_input('Username: ')
            if username == '':
                print "You must specify a valid user"
                return False
            rtn = self.core.is_friend(self.account, username)
            if rtn.code > 0:
                print rtn.errmsg
                return False
            if rtn.items:
                print "%s is following you" % username
            else:
                print "%s is not following you" % username
    
    def help_friend(self, desc=True):
        text = 'Manage user friends'
        if not desc:
            text = ''
        print '\n'.join([text,
           'Usage: friend <arg>\n',
            'Possible arguments are:',
            '  list:\t\t List all friends',
            '  follow:\t Follow user',
            '  unfollow:\t Unfollow friend',
            '  block:\t Block user',
            '  unblock:\t Unblock user',
            '  spammer:\t Report user as spammer',
            '  check:\t Verify if certain user is following you',
        ])
    
    def do_direct(self, arg):
        if not self.__validate_default_account(): 
            return False
        
        if not self.__validate_arguments(ARGUMENTS['direct'], arg): 
            self.help_direct(False)
            return False
        
        if arg == 'send':
            username = raw_input('Username: ')
            if username == '':
                print "You must specify a valid user"
                return False
            message = self.__build_message_menu()
            if not message:
                print 'You must to write something'
                return False
            
            rtn = self.core.send_direct(self.account, username, message)
            if rtn.code > 0:
                print rtn.errmsg
            else:
                print 'Direct message sent'
        elif arg == 'delete':
            dm_id = raw_input('Direct message ID: ')
            if dm_id == '':
                print "You must specify a valid id"
                return False
            rtn = self.core.destroy_direct(self.account, dm_id)
            if rtn.code > 0:
                print rtn.errmsg
            else:
                print 'Direct message deleted'
    
    def help_direct(self, desc=True):
        text = 'Manage user direct messages'
        if not desc:
            text = ''
        print '\n'.join([text,
           'Usage: direct <arg>\n',
            'Possible arguments are:',
            '  send:\t\t Send direct message',
            '  delete:\t Destroy direct message',
        ])
    
    def do_favorite(self, arg):
        if not self.__validate_default_account(): 
            return False
        
        if not self.__validate_arguments(ARGUMENTS['favorite'], arg): 
            self.help_status(False)
            return False
        
        if arg == 'mark':
            status_id = raw_input('Status ID: ')
            if status_id == '':
                print "You must specify a valid id"
                return False
            rtn = self.core.mark_favorite(self.account, status_id)
            if rtn.code > 0:
                print rtn.errmsg
            else:
                print 'Status marked as favorite'
        elif arg == 'unmark':
            status_id = raw_input('Status ID: ')
            if status_id == '':
                print "You must specify a valid id"
                return False
            rtn = self.core.unmark_favorite(self.account, status_id)
            if rtn.code > 0:
                print rtn.errmsg
            else:
                print 'Status unmarked as favorite'
    
    def help_favorite(self, desc=True):
        text = 'Manage favorite marks of statuses'
        if not desc:
            text = ''
        print '\n'.join([text,
           'Usage: direct <arg>\n',
            'Possible arguments are:',
            '  mark:\t\t Mark a status as favorite',
            '  unmark:\t Remove favorite mark from a status',
        ])
    
    def do_search(self, arg=None):
        if not self.__validate_default_account(): 
            return False
        
        if arg: 
            self.help_search()
            return False
        
        query = raw_input('Type what you want to search for: ')
        rtn = self.core.search(self.account, query)
        self.__show_statuses(rtn)
    
    def help_search(self):
        print 'Search for a pattern'
    
    def do_trends(self, arg=None):
        if not self.__validate_default_account(): 
            return False
        
        if arg: 
            self.help_trends()
            return False
        
        trends = self.core.trends(self.account)
        if trends.code > 0:
            print trends.errmsg
            return False
        
        for trend in trends:
            print trend.title
            print "=" * len(trend.title)
            for topic in trend.items:
                promoted = ''
                if topic.promoted:
                    promoted = '*'
                print "%s%s |" % (topic.name, promoted),
            print
    
    def help_trends(self):
        print 'Show global and local trends'
    
    def do_EOF(self, line):
        return self.do_exit('')
        
    def do_exit(self, line=None):
        print
        self.log.debug('Bye')
        return True
    
    def help_help(self):
        print 'Show help. Dah!'
        
    def help_exit(self):
        print 'Close the application'
    
    def help_EOF(self):
        print 'Close the application'
    
    def show_shorten_url(self, text):
        print "URL Cortada:", text

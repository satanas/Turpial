# -*- coding: utf-8 -*-

# Module to handle i18n
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import os
import logging
import gettext

log = logging.getLogger('Lang')
log.debug('Started')

# Initialize gettext
gettext_domain = 'turpial'
# localedir definition in development mode
if os.path.isdir(os.path.join(os.path.dirname(__file__), '..', 'i18n')):
    localedir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'i18n'))
    trans = gettext.install(gettext_domain, localedir)
    log.debug('LOCALEDIR: %s' % localedir)
else:
    trans = gettext.install(gettext_domain)

STRINGS = {
    'twitter': 'Twitter',
    'identica': 'Identi.ca',
    'welcome': _('Welcome to Turpial!'),
    'no_active_accounts': _('You have no active accounts. Please register your \
accounts and add some columns'),
    'about': _('About'),
    'preferences': _('Preferences'),
    'add_columns': _('Add columns'),
    'accounts_manager': _('Accounts Manager'),
    'update_status': _('Update status'),
    'accounts': _('Accounts'),
    'columns': _('Columns'),
    'column': _("Column"),
    'create_account': _('Create Account'),
    'connect': _('Connect'),
    'add': _('Add'),
    'reply': _('Reply'),
    'quote': _('Quote'),
    'retweet': _('Retweet'),
    '+fav': _('+Fav'),
    '-fav': _('-Fav'),
    'delete': _('Delete'),
    'tweet': _('Tweet'),
    'follow': _('Follow'),
    'exit': _('Exit'),
    'user': _('User'),
    'password': _('Password'),
    'protocol': _('Protocol'),
    'close': _('Close'),
    'save': _('Save'),
    'ok': _('Ok'),
    'cancel': _('Cancel'),
    'search': _('Search'),
    'public_timeline': _('Public Timeline'),
    'saving': _('Saving...'),
    'loading': _('Loading...'),
    'connecting': _('Connecting...'),
    'authenticating': _('Authenticating...'),
    'authorizing': _('Authorizing...'),
    'secure_auth': _('Secure Authentication'),
    'authorize_turpial': _('Autorize Turpial, copy the PIN in the \
text box below and click OK:'),
    'login_cancelled': _('Login cancelled by user'),
    'invalid_pin': _('You must write a valid PIN'),
    'delete_account_confirm': _("Do you really want to delete the account "),
    'delete_column_confirm': _("Do you really want to delete the column "),
    'fields_cant_be_empty': _("Fields can't be empty"),
    'from': _("from"),
    'in_reply_to': _("in reply to"),
    'people': _("people"),
    'person': _("person"),
    'retweeted_by': _("Retweeted by"),
    'no_column_yet': _("There are no available columns because I'm still logging in"),
    'whats_happening': _("What's happening?"),
    'retweeting': _("Retweeting..."),
    'successfully_retweeted': _("Sucessfully retweeted"),
    'adding_to_fav': _("Adding to favorites..."),
    'removing_from_fav': _("Removing from favorites..."),
}

class i18n:
    @staticmethod
    def get(key):
        try:
            return STRINGS[key]
        except KeyError:
            return key

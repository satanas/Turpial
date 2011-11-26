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
    'account': _('Accounts'),
    'columns': _('Columns'),
    'create_account': _('Create Account'),
    'connect': _('Connect'),
    'about': _('About'),
    'preferences': _('Preferences'),
    'add_account': _('Add account'),
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
    'fields_cant_be_empty': _("Fields can't be empty"),
    'from': _("from"),
    'in_reply_to': _("in reply to"),
    'people': _("people"),
    'person': _("person"),
    'retweeted_by': _("Retweeted by"),
}

class i18n:
    @staticmethod
    def get(key):
        try:
            return STRINGS[key]
        except KeyError:
            return key

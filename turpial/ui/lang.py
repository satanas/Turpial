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
    'accounts': _('Accounts'),
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
    'connecting': _('Connecting...'),
    #'connecting': _('Connecting...'),
    'secure_auth': _('Secure Authentication'),
    'login_cancelled': _('Login cancelled by user'),
    
    'delete_account_confirm': _("Do you really want to delete the account "),
    'fields_cant_be_empty': _("Fields can't be empty"),
}
    
class i18n:
    @staticmethod
    def get(key):
        try:
            return STRINGS[key]
        except KeyError:
            return key

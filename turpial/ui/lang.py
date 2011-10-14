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
    'login_at_startup': _('Login at startup'),
    'connect': _('Connect'),
    'about': _('About'),
    'preferences': _('Preferences'),
    'add_account': _('Add account'),
    'user_and_password': _('User and Password'),
    'remember_credentials': _('Remember my credentials'),
    'tweet': _('Tweet'),
    'follow': _('Follow'),
    'exit': _('Exit'),
    'connecting': _('Connecting...'),
    'user_and_password': _('User and Password'),
    'protocol': _('Protocol'),
    'password': _('Password'),
    'remember_credentials': _('Remember my credentials'),
    'close': _('Close'),
    'save': _('Save'),
    'ok': _('Ok'),
    'cancel': _('Cancel'),
    'saving': _('Saving...'),
    'fields_cant_be_empty': _("Fields can't be empty"),
    'one_account_to_login': _("Select at least one account to login"),
    'type_password': _("Type the password for %s (%s)"),
    'credentials': _("Credentials"),
    'remember_my_credentials': _('Remember my credentials'),
    'login_cancelled': _('Login cancelled by user'),
}
    
class i18n:
    @staticmethod
    def get(key):
        try:
            return STRINGS[key]
        except KeyError:
            return key

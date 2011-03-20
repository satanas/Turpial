# -*- coding: utf-8 -*-

"""Implementación del módulo para peticiones HTTP adaptado a Identi.ca"""
#
# Author: Wil Alvarez (aka Satanas)
# Jun 08, 2010

import urllib2
import logging
import traceback

from turpial.api.interfaces.http import TurpialHTTP, TurpialException
from turpial.api.protocols.identica.globals import POST_ACTIONS


class IdenticaHTTP(TurpialHTTP):
    def __init__(self):
        TurpialHTTP.__init__(self, POST_ACTIONS)
        self.log = logging.getLogger('IdenticaHTTP')
        
    def request(self, uri, args={}):
        try:
            rtn = self.do_request(uri, args)
            return rtn
        except urllib2.HTTPError, exc:
            self.log.debug(("HTTPError for URL: %s\nparameters: (%s)\n"
                           "details: %s") % (uri, args, traceback.print_exc()))
            if (exc.code == 304):
                return []
            elif (exc.code == 400):
                raise TurpialException(_('Sorry, you don\'t have more API'
                                         'calls'))
            elif (exc.code == 401):
                raise TurpialException(_('Invalid credentials'))
            elif (exc.code == 403):
                rtn = exc.read()
                print 'Error 403:', rtn
                if rtn.find("Status is a duplicate.") > 0:
                    msg = _('Your status was sent. Don\'t try again')
                elif rtn.find("is already on your list.") > 0:
                    msg = _('%s already is a friend')
                else:
                    msg = _('Hey! You are over the limit of API calls')
                raise TurpialException(msg)
            elif (exc.code == 404):
                raise TurpialException(_('Err... invalid request'))
            elif (exc.code == 406):
                raise TurpialException(_('You are searching a very weird thing'))
            elif (exc.code == 420):
                raise TurpialException(_('You are searching too much!'))
            elif (exc.code == 500):
                raise TurpialException(_('Oops! Something went wrong'))
            elif (exc.code == 502):
                raise TurpialException(_('Twitter is down. Try again later'))
            elif (exc.code == 503):
                raise TurpialException(_('Twitter is overcapacity'))
        except urllib2.URLError, exc:
            self.log.debug(
                "URLError for URL: %s\nparameters: (%s)\ndetails: %s" % (
                                uri, args, traceback.print_exc()
                )
            )
            raise TurpialException(_('Can\'t connect to Twitter'))
        except Exception, exc:
            self.log.debug(
                "Unknown error for URL: %s\nparameters: (%s)\ndetails: %s" % (
                    uri, args, traceback.print_exc()
                )
            )
            raise TurpialException(exc)

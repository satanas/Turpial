# -*- coding: utf-8 -*-

"""Implementación del módulo para peticiones HTTP adaptado a Twitter"""
#
# Author: Wil Alvarez (aka Satanas)
# May 26, 2010

import urllib2
import logging
import traceback

from turpial.api.interfaces.http import TurpialHTTP, TurpialException
from turpial.api.protocols.twitter.twitter_globals import POST_ACTIONS

class TwitterHTTP(TurpialHTTP):
    def __init__(self):
        TurpialHTTP.__init__(self, POST_ACTIONS)
        self.log = logging.getLogger('TwitterHTTP')
        
    def _simple_request(self, uri, args={}):
        try:
            req = self._build_simple_request(uri, args)
            rtn = self._execute_simple_request(req)
            return rtn
        except urllib2.HTTPError, exc:
            self.log.debug("HTTPError for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            if (exc.code == 304):
                return []
            elif (exc.code == 400):
                raise TurpialException('Err... invalid request')
            elif (exc.code == 401):
                raise TurpialException('Invalid username/password')
            elif (exc.code == 403):
                raise TurpialException('Hey! You are over the limit of API calls')
            elif (exc.code == 404):
                raise TurpialException('Err... invalid request')
            elif (exc.code == 406):
                raise TurpialException('You are searching a very weird thing')
            elif (exc.code == 420):
                raise TurpialException('You are searching too much!')
            elif (exc.code == 500):
                raise TurpialException('Oops! Something went wrong')
            elif (exc.code == 502):
                raise TurpialException('Twitter is down. Try again later')
            elif (exc.code == 503):
                raise TurpialException('Twitter is overcapacity')
        except urllib2.URLError, exc:
            self.log.debug("URLError for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            raise TurpialException('Can\'t connect to Twitter')
        except Exception, exc:
            self.log.debug("Unknown error for URL: %s\nparameters: (%s)\n\
details: %s" % (uri, args, traceback.print_exc()))
            raise TurpialException(e)

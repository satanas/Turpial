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
        except urllib2.HTTPError, e:
            if (e.code == 304):
                return []
            elif (e.code == 400) or (e.code == 403):
                raise TurpialException('Hey! You are over the limit of API calls')
            elif (e.code == 401):
                raise TurpialException('Invalid username/password')
            elif (e.code == 404):
                raise TurpialException('Err... invalid request')
            elif (e.code == 406):
                raise TurpialException('You are searching a very weird thing')
            elif (e.code == 420):
                raise TurpialException('You are searching too much!')
            elif (e.code == 500):
                raise TurpialException('Oops! Something went wrong')
            elif (e.code == 502):
                raise TurpialException('Twitter is down. Try again later')
            elif (e.code == 503):
                raise TurpialException('Twitter is overcapacity')
        except urllib2.URLError, e:
            raise TurpialException('Can\'t connect to Twitter')
        except Exception, e:
            self.log.debug("Unknown error for URL: %s\nparameters: (%s)\n\
                details: %s" % (uri, args, traceback.print_exc()))
            raise TurpialException(e)

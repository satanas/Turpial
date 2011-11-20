# -*- coding: utf-8 -*-

# Base class for all the Turpial interfaces
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import logging
import webbrowser
import subprocess

class Base:
    '''Parent class for every UI interface'''
    def __init__(self, core, config):
        self.core = core
        self.config = config
        self.log = logging.getLogger('UI')
        self.log.debug('Started')
    
    # ------------------------------------------------------------
    # Common methods to all interfaces
    # ------------------------------------------------------------
    
    def open_url(self, url):
        '''Open a URL in the configured web browser'''
        browser = self.config.read('Browser', 'cmd')
        if browser != '':
            self.log.debug('Opening URL %s with %s' % (url, browser))
            subprocess.Popen([browser, url])
        else:
            #if not url.startswith('http'):
            #    url = 'http://' + url
            self.log.debug('Opening URL %s with default browser' % url)
            webbrowser.open(url)

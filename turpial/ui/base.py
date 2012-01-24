# -*- coding: utf-8 -*-

# Base class for all the Turpial interfaces
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import logging
import webbrowser
import subprocess

MIN_WINDOW_WIDTH = 250

class Base:
    '''Parent class for every UI interface'''
    def __init__(self, core):
        self.core = core
        self.log = logging.getLogger('UI')
        self.log.debug('Started')
    
    # ------------------------------------------------------------
    # Common methods to all interfaces
    # ------------------------------------------------------------
    
    def open_url(self, url):
        '''Open a URL in the configured web browser'''
        browser = self.core.get_default_browser()
        if browser != '':
            self.log.debug('Opening URL %s with %s' % (url, browser))
            subprocess.Popen([browser, url])
        else:
            #if not url.startswith('http'):
            #    url = 'http://' + url
            self.log.debug('Opening URL %s with default browser' % url)
            webbrowser.open(url)
    
    def count_new_statuses(self, last, current):
        if not last:
            return len(current)
        
        count = 0
        for st in last:
            for ss in current:
                if ss.id_ == st.id_:
                    break
            count += 1
        return count
    
    def save_window_geometry(self, width, height):
        pass

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

    # TODO: Put this in util.py
    def humanize_size(self, size):
        if size == 0:
            return '0 B'

        kbsize = size / 1024
        if kbsize > 0:
            mbsize = kbsize / 1024
            if mbsize > 0:
                gbsize = mbsize / 1024
                if gbsize > 0:
                    return "%.2f GB" % (mbsize / 1024.0)
                else:
                    return "%.2f MB" % (kbsize / 1024.0)
            else:
                return "%.2f KB" % (size / 1024.0)
        else:
            return "%.2f B" % size
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

    def get_new_statuses(self, current, last):
        if not current:
            return len(last)
        if not last:
            return 0

        count = 0
        our_last_status_id = current[0].id_

        for last_status in last:
            if last_status.id_ != our_last_status_id:
                count +=1
            else:
                break

        return count

    def save_window_geometry(self, width, height):
        pass

    def get_config(self):
        return self.core.get_config()

    def save_config(self, new_config):
        self.core.save_all_config(new_config)

    def get_filters(self):
        return self.core.list_filters()

    def save_filters(self, lst):
        self.core.save_filters(lst)

    def restore_default_config(self):
        self.core.delete_current_config()

    def delete_all_cache(self):
        self.core.delete_cache()

    def get_cache_size(self):
        return self.humanize_size(self.core.get_cache_size())

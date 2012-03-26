# -*- coding: utf-8 -*-

# Widget for HTML view in Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import os
#import gtk
#import webkit
#import gobject
from PyQt4 import QtWebKit
from PyQt4.QtCore import QObject,pyqtSignal
from PyQt4.QtWebKit import QWebPage

class HtmlView(QObject):

    action_request = pyqtSignal(str)
    link_request = pyqtSignal(str)
    def __init__(self, coding='utf-8'):
        super(HtmlView,self).__init__()
        self.coding = coding
        self.uri = 'file://' + os.path.dirname(__file__)
        self.view = QtWebKit.QWebView()
        self.view.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.view.page().linkClicked.connect(self.__process)
        
#        self.settings = webkit.WebSettings()
#        self.settings.set_property('enable-default-context-menu', False)

#       self.settings.enable_java_applet = False
#        self.settings.enable_plugins = False
#        self.settings.enable_page_cache = False
#        self.settings.enable_offline_web_application_cache = False
#        self.settings.enable_html5_local_storage = False
#        self.settings.enable_html5_database = False
#        self.settings.enable_default_context_menu = False
#        self.settings.enable_xss_auditor = False
#        self.settings.enable_dns_prefetching = False
#        self.settings.resizable_text_areas = False
#        self.settings.web_security_enabled = False

#        self.view = webkit.WebView()
#        self.view.set_settings(self.settings)
#        self.view.connect('load-started', self.__started)
#        self.view.connect('load-finished', self.__finished)
#        self.view.connect('console-message', self.__console_message)
#        self.view.connect('navigation-policy-decision-requested', self.__process)

#        scroll = gtk.ScrolledWindow()
#        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
#        scroll.set_shadow_type(gtk.SHADOW_IN)
#        scroll.add(self.view)

#        self.pack_start(scroll, True, True, 0)

    def __console_message(self, view, message, line, source_id, data=None):
        print "%s <%s:%i>" % (message, source_id, line)
        return True

    def __process(self, url):
        print "entrando __process"
        url = str(url.toString())
        if url is None:
            pass
        elif url.startswith('cmd:'):
            print "a emitir action"
            #policy.ignore()
            #self.emit('action-request', url[4:])
            self.action_request.emit(url[4:])

        elif url.startswith('link:'):
            print "a emitir link"
            #policy.ignore()
            #self.emit('link-request', url[5:])
            self.link_request.emit(url[4:])
        #policy.use()

    def __started(self, widget, frame):
        self.emit('load-started')

    def __finished(self, widget, frame):
        self.emit('load-finished')

    def load(self, url):
        gobject.idle_add(self.view.load_uri, url)

    def render(self, html):
        #gobject.idle_add(self.view.load_string, html, "text/html", self.coding,
            #self.uri)
        self.view.setHtml(html)

    def update_element(self, id_, html, extra=''):
        html = html.replace('"', '\\"')
        script = "$('%s').html(\"%s\"); %s" % (id_, html, extra)
        #fd = open('/tmp/traceback', 'w')
        #fd.write(script)
        #fd.close()
        self.execute(script)

    def remove_element(self, id_):
        script = "$('%s').remove();" % (id_)
        self.execute(script)

    def append_element(self, id_, html, extra=''):
        html = html.replace('"', '\\"')
        script = "$('%s').append(\"%s\"); %s" % (id_, html, extra)
        self.execute(script)

    def prepend_element(self, id_, html, extra=''):
        html = html.replace('"', '\\"')
        script = "$('%s').prepend(\"%s\"); %s" % (id_, html, extra)
        self.execute(script)

    def execute(self, script, sanitize=False):
        script = script.replace('\n', ' ')
        self.view.execute_script(script)

    def stop(self):
        self.view.stop_loading()

#gobject.type_register(HtmlView)

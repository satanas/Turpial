# -*- coding: utf-8 -*-

# Widget for HTML view in Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 09, 2011

import gtk
import webkit
import gobject

class HtmlView(gtk.VBox, gobject.GObject):
    __gsignals__ = {
        "action-request": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
        "link-request": (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, )),
    }
    
    def __init__(self, uri, coding='utf-8'):
        gobject.GObject.__init__(self)
        gtk.VBox.__init__(self, False)
        
        self.coding = coding
        self.uri = uri
        self.settings = webkit.WebSettings()
        self.settings.set_property('enable-default-context-menu', False)
        
        self.view = webkit.WebView()
        self.view.set_settings(self.settings)
        #self.view.connect('load-started', self.__started)
        #self.view.connect('load-finished', self.__finished)
        self.view.connect('navigation-policy-decision-requested', self.__process)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.view)
        
        self.pack_start(scroll, True, True, 0)
    
    def __process(self, view, frame, request, action, policy, data=None):
        url = request.get_uri()
        if url is None:
            pass
        elif url.startswith('cmd:'):
            policy.ignore()
            self.emit('action-request', url[4:])
        elif url.startswith('http:'):
            policy.ignore()
            self.emit('link-request', url)
        policy.use()
    
    def render(self, html):
        gobject.idle_add(self.view.load_string, html, "text/html", self.coding, 
            self.uri)
    
    def execute(self, script):
        self.view.execute_script(script)

gobject.type_register(HtmlView)

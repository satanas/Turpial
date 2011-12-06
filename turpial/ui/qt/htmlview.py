# -*- coding: utf-8 -*-

# QT main view for Turpial
#
# Author:  Carlos Guerrero (aka guerrerocarlos)
# Started: Sep 11, 2011

import os
from PyQt4 import QtWebKit

class HtmlView(QtWebKit.QWebView):
    
    def __init__(self, coding='utf-8'):
        super(HtmlView,self).__init__() 
        self.coding = coding
        self.uri = 'file://' + os.path.dirname(__file__)
        
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
        self.setHtml(html)
    
    def update_element(self, id_, html):
        html = html.replace('"', '\\"')
        html = html.replace('\n', " \\\n")
        script = "$('#%s').html(\"%s\");" % (id_, html)
        print script
        self.view.execute_script(script)
        self.view.execute_script('after_update();')
        
    def execute(self, script):
        self.view.execute_script(script)


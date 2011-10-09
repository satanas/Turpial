# -*- coding: utf-8 -*-

# Webkit container for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 05, 2011

import re
import os
import gtk
import webkit
import gobject

from turpial.ui.lang import i18n

DATA_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
IMAGES_DIR = os.path.join(DATA_DIR, 'pixmaps')
LAYOUT_DIR = os.path.join(DATA_DIR, 'layout')
JS_LAYOUT_DIR = os.path.join(LAYOUT_DIR, 'js')
CSS_LAYOUT_DIR = os.path.join(LAYOUT_DIR, 'css')

DEFAULT_THEMES_DIR = os.path.realpath(os.path.join(DATA_DIR, 'themes', 'default'))
DEFAULT_IMAGES_DIR = os.path.realpath(os.path.join(DEFAULT_THEMES_DIR, 'images'))
DEFAULT_JS_DIR = os.path.realpath(os.path.join(DEFAULT_THEMES_DIR, 'js'))
DEFAULT_CSS_DIR = os.path.realpath(os.path.join(DEFAULT_THEMES_DIR, 'css'))

IMG_PATTERN = re.compile('(<% img [\'"](.*?)[\'"] %>)')
CSS_IMG_PATTERN = re.compile('(<% css_img [\'"](.*?)[\'"] %>)')
PARTIAL_PATTERN = re.compile('(<% partial [\'"](.*?)[\'"] %>)')
I18N_PATTERN = re.compile('(<% \$(.*?) %>)')

class WebContainer(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False)
        
        self.settings = webkit.WebSettings()
        self.settings.set_property('enable-default-context-menu', False)
        
        self.view = webkit.WebView()
        self.view.set_settings(self.settings)
        #self.view.connect('load-started', self.__started)
        #self.view.connect('load-finished', self.__finished)
        self.view.connect('navigation-policy-decision-requested', self.__test)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.view)
        
        self.pack_start(scroll, True, True, 0)
        
        self.scripts = []
        self.styles = []
        self.partials = {}
    
    def __test(self, view, frame, request, action, policy, data=None):
        print 'frame:', frame
        print 'request:', request
        print 'action:', action
        print 'policy:', policy
        url = request.get_uri()
        print url
        if url is None:
            pass
        elif url.startswith('cmd:'):
            self.callback(url[4:])
            policy.ignore()
        elif url.startswith('http:'):
            policy.ignore()
        policy.use()
    
    def __load_app_layout(self):
        self.app_layout = self.open_layout_template('app')
    
    def set_action_callback(self, callback):
        self.callback = callback
        
    def load_layout(self, res):
        self.app_layout = self.__open_template(res)
        
        # Load default js
        for js in ['jquery']:
            filepath = os.path.realpath(os.path.join(JS_LAYOUT_DIR, js + '.js'))
            self.scripts.append(filepath)
        
        # Load default css
        for css in ['common']:
            filepath = os.path.realpath(os.path.join(CSS_LAYOUT_DIR, css + '.css'))
            self.styles.append(filepath)
        
        js_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'js', res + '.js'))
        if os.path.isfile(js_file):
            self.scripts.append(js_file)
        
        css_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'css', res + '.css'))
        if os.path.isfile(css_file):
            self.styles.append(css_file)
    
    def __open_template(self, res):
        filepath = os.path.realpath(os.path.join(LAYOUT_DIR, res + '.template'))
        fd = open(filepath, 'r')
        resource = fd.read()
        fd.close()
        return resource
    
    def __open_partial(self, name):
        filepath = os.path.join(LAYOUT_DIR, name + '.partial')
        fd = open(filepath, 'r')
        resource = fd.read()
        fd.close()
        return resource
        
    def open_theme_resource(self, res):
        filepath = os.path.realpath(os.path.join(DEFAULT_THEMES_DIR, res))
        fd = open(filepath, 'r')
        resource = fd.read()
        fd.close()
        return resource
        
    def add_javascript(self, filename):
        filepath = os.path.realpath(os.path.join(DEFAULT_JS_DIR, filename + '.js'))
        self.scripts.append(filepath)
    
    def add_style(self, filename):
        filepath = os.path.realpath(os.path.join(DEFAULT_CSS_DIR, filename + '.css'))
        self.styles.append(filepath)
        
    def javascript_tag(self, filepath):
        return "<script type='text/javascript' src='file://%s'></script>" % filepath
        
    def stylesheet_tag(self, filepath):
        return "<link rel='stylesheet' type='text/css' href='file://%s'>" % filepath
        
    def image_tag(self, filename, base=True):
        if base:
            filepath = os.path.realpath(os.path.join(IMAGES_DIR, filename))
        else:
            filepath = os.path.realpath(os.path.join(DEFAULT_IMAGES_DIR, filename))
        
        return "<img src='file://%s'/>" % filepath
    
    def render(self):
        page = self.app_layout
        
        js_tags = ''
        for js in self.scripts:
            js_tags += self.javascript_tag(js) + '\n'
        page = page.replace('<% javascripts %>', js_tags)
        
        css_tags = '<style type="text/css">'
        for css in self.styles:
            fd = open(css, 'r')
            resource = fd.read()
            fd.close()
            css_tags += resource + '\n'
        css_tags += '</style>'
        page = page.replace('<% stylesheets %>', css_tags)
        
        for part in PARTIAL_PATTERN.findall(page):
            page = page.replace(part[0], self.partials[part[1]])
        
        for img in IMG_PATTERN.findall(page):
            page = page.replace(img[0], self.image_tag(img[1]))
        
        for img in CSS_IMG_PATTERN.findall(page):
            filepath = os.path.realpath(os.path.join(IMAGES_DIR, img[1]))
            page = page.replace(img[0], 'file://' + filepath)
            
        for text in I18N_PATTERN.findall(page):
            # TODO: Escape invalid characters
            page = page.replace(text[0], i18n.get(text[1]))
        
        print page
        gobject.idle_add(self.view.load_string, page, "text/html", "iso-8859-15", 'file://' + os.path.dirname(__file__))
    
    def show_login(self, accounts):
        self.load_layout('login')
        
        self.partials['accounts'] = ''
        partial = self.__open_partial('account')
        for acc in accounts:
            section = partial.replace('<% @account_id %>', acc)
            section = section.replace('<% @account_name %>', acc.split('-')[0])
            section = section.replace('@protocol', acc.split('-')[1] + '.png')
            self.partials['accounts'] += section + '\n'
        
        self.render()

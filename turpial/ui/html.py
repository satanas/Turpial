# -*- coding: utf-8 -*-

# Webkit container for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 05, 2011

import re
import os

from turpial.ui.lang import i18n

DATA_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'data'))
IMAGES_DIR = os.path.join(DATA_DIR, 'pixmaps')
LAYOUT_DIR = os.path.join(DATA_DIR, 'layout')
JS_LAYOUT_DIR = os.path.join(LAYOUT_DIR, 'js')
CSS_LAYOUT_DIR = os.path.join(LAYOUT_DIR, 'css')

IMG_PATTERN = re.compile('(<% img [\'"](.*?)[\'"] %>)')
CSS_IMG_PATTERN = re.compile('(<% css_img [\'"](.*?)[\'"] %>)')
PARTIAL_PATTERN = re.compile('(<% partial [\'"](.*?)[\'"] %>)')
I18N_PATTERN = re.compile('(<% \$(.*?) %>)')

class HtmlParser:
    def __init__(self):
        self.scripts = []
        self.styles = []
        self.partials = {}
    
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
    
    def __load_layout(self, res):
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
        
    def add_javascript(self, filename):
        filepath = os.path.realpath(os.path.join(DEFAULT_JS_DIR, filename + '.js'))
        self.scripts.append(filepath)
    
    def add_style(self, filename):
        filepath = os.path.realpath(os.path.join(DEFAULT_CSS_DIR, filename + '.css'))
        self.styles.append(filepath)
        
    def __javascript_tag(self, filepath):
        return "<script type='text/javascript' src='file://%s'></script>" % filepath
        
    def __image_tag(self, filename, base=True):
        if base:
            filepath = os.path.realpath(os.path.join(IMAGES_DIR, filename))
        else:
            filepath = os.path.realpath(os.path.join(DEFAULT_IMAGES_DIR, filename))
        
        return "<img src='file://%s'/>" % filepath
    
    def __render(self):
        page = self.app_layout
        
        js_tags = ''
        for js in self.scripts:
            js_tags += self.__javascript_tag(js) + '\n'
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
            page = page.replace(img[0], self.__image_tag(img[1]))
        
        for img in CSS_IMG_PATTERN.findall(page):
            filepath = os.path.realpath(os.path.join(IMAGES_DIR, img[1]))
            page = page.replace(img[0], 'file://' + filepath)
            
        for text in I18N_PATTERN.findall(page):
            # TODO: Escape invalid characters
            page = page.replace(text[0], i18n.get(text[1]))
        
        print page
        return page
    
    def login(self, accounts):
        self.__load_layout('login')
        
        self.partials['accounts'] = ''
        partial = self.__open_partial('account')
        for acc in accounts:
            section = partial.replace('<% @account_id %>', acc)
            section = section.replace('<% @account_name %>', acc.split('-')[0])
            section = section.replace('@protocol', acc.split('-')[1] + '.png')
            self.partials['accounts'] += section + '\n'
        
        return self.__render()

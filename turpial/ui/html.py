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
RESIZED_IMG_PATTERN = re.compile('(<% rimg [\'"](.*?)[\'"], (.*?), (.*?) %>)')
CSS_IMG_PATTERN = re.compile('(<% css_img [\'"](.*?)[\'"] %>)')
PARTIAL_PATTERN = re.compile('(<% partial [\'"](.*?)[\'"] %>)')
I18N_PATTERN = re.compile('(<% \$(.*?) %>)')

class HtmlParser:
    def __init__(self, protocols):
        self.scripts = []
        self.styles = []
        self.partials = {}
        self.protocols = protocols
    
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
        self.scripts = []
        self.styles = []
        self.partials = {}
        
        self.app_layout = self.__open_template(res)
        
        # Load default js
        
        for js in ['jquery', 'common']:
            filepath = os.path.realpath(os.path.join(JS_LAYOUT_DIR, js + '.js'))
            self.scripts.append(filepath)
        
        # Load default css
        for css in ['common', 'notice']:
            filepath = os.path.realpath(os.path.join(CSS_LAYOUT_DIR, css + '.css'))
            self.styles.append(filepath)
        
        js_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'js', res + '.js'))
        if os.path.isfile(js_file):
            self.scripts.append(js_file)
        
        css_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'css', res + '.css'))
        if os.path.isfile(css_file):
            self.styles.append(css_file)
        
    def __image_tag(self, filename, base=True, width=None, height=None):
        if base:
            filepath = os.path.realpath(os.path.join(IMAGES_DIR, filename))
        else:
            filepath = os.path.realpath(os.path.join(DEFAULT_IMAGES_DIR, filename))
        
        if width and height:
            return "<img src='file://%s' width='%s' height='%s' />" % (filepath, width, height)
        else:
            return "<img src='file://%s'/>" % filepath
    
    def __parse_tags(self, page):
        for part in PARTIAL_PATTERN.findall(page):
            page = page.replace(part[0], self.partials[part[1]])
        
        for img in IMG_PATTERN.findall(page):
            page = page.replace(img[0], self.__image_tag(img[1]))
        
        for img in RESIZED_IMG_PATTERN.findall(page):
            page = page.replace(img[0], self.__image_tag(img[1], width=img[2], height=img[3]))
            
        for img in CSS_IMG_PATTERN.findall(page):
            filepath = os.path.realpath(os.path.join(IMAGES_DIR, img[1]))
            page = page.replace(img[0], 'file://' + filepath)
            
        for text in I18N_PATTERN.findall(page):
            # TODO: Escape invalid characters
            page = page.replace(text[0], i18n.get(text[1]))
        return page
        
    def __render(self):
        page = self.app_layout
        
        js_tags = '<script type="text/javascript">'
        for js in self.scripts:
            fd = open(js, 'r')
            resource = fd.read()
            fd.close()
            js_tags += resource + '\n'
        js_tags += '</script>'
        page = page.replace('<% javascripts %>', js_tags)
        
        css_tags = '<style type="text/css">'
        for css in self.styles:
            fd = open(css, 'r')
            resource = fd.read()
            fd.close()
            css_tags += resource + '\n'
        css_tags += '</style>'
        page = page.replace('<% stylesheets %>', css_tags)
        
        page = self.__parse_tags(page)
        #print page
        return page
    
    def main(self, accounts, columns):
        self.__load_layout('main')
        if len(columns) == 0:
            dock = ''
            content = self.__open_partial('empty')
        else:
            content = ''
            dock = self.__open_partial('dock')
            for i in range(len(columns)):
                acc_name = columns[i].split('-')[0]
                col_name = columns[i].split('-')[2].capitalize()
                protocol_img = columns[i].split('-')[1] + '.png'
                label = "%s :: %s" % (acc_name, col_name)
                
                col_content = self.__open_partial('column_content')
                col_content = col_content.replace('<% @column_id %>', str(i + 1))
                col_content = col_content.replace('<% @column_label %>', label)
                col_content = col_content.replace('@protocol_img', protocol_img)
                
                col = self.__open_partial('column')
                col = col.replace('<% @column_id %>', str(i + 1))
                col = col.replace('<% @column_content %>', col_content)
                content += col
        self.app_layout = self.app_layout.replace('<% @dock %>', dock)
        self.app_layout = self.app_layout.replace('<% @content %>', content)
        
        return self.__render()
        
    def accounts(self, accounts):
        self.__load_layout('accounts')
        acc_list = self.render_account_list(accounts)
        self.app_layout = self.app_layout.replace('<% @accounts %>', acc_list)
        return self.__render()
        
    def account_form(self, plist, user='', pwd='', prot=''):
        self.__load_layout('account_form')
        protocols = '<option value="null">-- Select --</option>'
        for pt in plist:
            checked = ''
            if pt == prot:
                checked = 'checked="checked"'
            protocols += '<option value="%s" %s>%s</option>' % (pt, checked, pt.capitalize())
        
        self.app_layout = self.app_layout.replace('<% @user %>', user)
        self.app_layout = self.app_layout.replace('<% @pwd %>', pwd)
        self.app_layout = self.app_layout.replace('<% @protocols %>', protocols)
        return self.__render()
        
    def render_account_list(self, accounts):
        self.partials['accounts'] = ''
        partial = self.__open_partial('account')
        for acc in accounts:
            passwd = ''
            if acc.profile.password:
                passwd = acc.profile.password
            section = partial.replace('<% @account_id %>', acc.id_)
            section = section.replace('<% @account_name %>', acc.profile.username)
            section = section.replace('<% @passwd %>', passwd)
            section = section.replace('<% @protocol_id %>', acc.id_.split('-')[1])
            section = section.replace('@protocol_img', acc.id_.split('-')[1] + '.png')
            
            self.partials['accounts'] += section + '\n'
        page = self.__parse_tags(self.partials['accounts'])
        
        return page
    
    def render_credentials_dialog(self, acc_id):
        user = acc_id.split('-')[0]
        protocol = acc_id.split('-')[1].capitalize()
        self.__load_layout('dialog-credentials')
        text = i18n.get('please_type_password') % (user, protocol)
        self.app_layout = self.app_layout.replace('<% @type_password %>', text)
        return self.__render()
        

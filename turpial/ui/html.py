# -*- coding: utf-8 -*-

# Webkit container for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 05, 2011

import re
import os

from turpial.ui.lang import i18n
from libturpial.common import ARG_SEP

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
        self.scripts = []
        self.styles = []
        self.partials = {}
        
        self.app_layout = self.__open_template(res)
        
        # Load default js
        
        for js in ['jquery', 'common']:
            filepath = os.path.realpath(os.path.join(JS_LAYOUT_DIR, js + '.js'))
            self.scripts.append(filepath)
        
        # Load default css
        for css in ['common']: #'grids-min', , 'notice'
            filepath = os.path.realpath(os.path.join(CSS_LAYOUT_DIR, css + '.css'))
            self.styles.append(filepath)
        
        js_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'js', res + '.js'))
        if os.path.isfile(js_file):
            self.scripts.append(js_file)
        
        css_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'css', res + '.css'))
        if os.path.isfile(css_file):
            self.styles.append(css_file)
        
    def __image_tag(self, filename, base=True, width=None, height=None, class_=None):
        if base:
            filepath = os.path.realpath(os.path.join(IMAGES_DIR, filename))
        else:
            filepath = os.path.realpath(os.path.join(DEFAULT_IMAGES_DIR, filename))
        
        class_tag = ''
        if class_:
            class_tag = "class='%s'" % class_
        
        if width and height:
            return "<img src='file://%s' width='%s' height='%s' %s/>" % (filepath, width, height, class_tag)
        else:
            return "<img src='file://%s' %s/>" % (filepath, class_tag)
    
    def __query_tag(self):
        return "<img style='display:none;' id='query' src='' alt='' />"
    
    def __verified_tag(self, verified):
        if verified:
            return self.__image_tag("mark-verified.png", 16, 16, class_='mark')
        else:
            return ''
    
    def __protected_tag(self, protected):
        if protected:
            return self.__image_tag("mark-locked.png", 16, 16, class_='mark')
        else:
            return ''
    
    def __reposted_tag(self, reposted):
        if reposted:
            return self.__image_tag("mark-repeated.png", 16, 16, class_='mark')
        else:
            return ''
    
    def __favorite_tag(self, favorite, status_id):
        if favorite:
            cmd = "cmd:unfav:%s" % status_id
            icon = self.__image_tag("mark-favorite.png", 16, 16, class_='star')
        else:
            cmd = "cmd:fav:%s" % status_id
            icon = self.__image_tag("mark-unfavorite.png", 16, 16, class_='star')
        
        return "<a href='%s'>%s</a>" % (cmd, icon)
    
    def __highlight_username(self, status):
        url = status.username + ARG_SEP + status.account_id
        return '<a href="cmd:show_profile:%s">%s</a>' % (url, status.username)

    def __highlight_hashtags(self, status, text):
        for h in status.entities['hashtags']:
            cad = '<a href="cmd:show_hashtag:%s">%s</a>' % (h.url, h.display_text)
            text = text.replace(h.search_for, cad)
        return text
    
    def __highlight_groups(self, status, text):
        for h in status.entities['groups']:
            cad = '<a href="cmd:show_group:%s">%s</a>' % (h.url, h.display_text)
            text = text.replace(h.search_for, cad)
        return text
    
    def __highlight_mentions(self, status, text):
        for h in status.entities['mentions']:
            cad = '<a href="cmd:show_profile:%s">%s</a>' % (h.url, h.display_text)
            text = text.replace(h.search_for, cad)
        return text
        
    def __highlight_urls(self, status, text):
        for url in status.entities['urls']:
            if url.url == None:
                url.url = url.search_for
            if url.url[0:7] != "http://":
                url.url = "http://%s" % url.url
            cad = '<a href="link:%s">%s</a>' % (url.url, url.display_text)
            text = text.replace(url.search_for, cad)
        return text
    
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
        
        page = page.replace('<% query %>', self.__query_tag())

        page = self.__parse_tags(page)
        return page
    
    def parse_command(self, command):
        action = command.split(':')[0]
        try:
            args = command.split(':')[1].split(ARG_SEP)
        except IndexError:
            args = []
        return action, args
    
    def empty(self):
        self.__load_layout('empty')
        return self.__render()
    
    def main(self, accounts, columns):
        self.__load_layout('main')
        content = ''
        for column in columns:
            content += self.render_column(column)
        self.app_layout = self.app_layout.replace('<% @content %>', content)
        
        page = self.__render()
        # TODO: Look for a better way of handle javascript code from python
        page = page.replace('<% @num_columns %>', str(len(columns)))
        return page
        
    def accounts(self, accounts):
        self.__load_layout('accounts')
        acc_list = self.render_account_list(accounts)
        self.app_layout = self.app_layout.replace('<% @accounts %>', acc_list)
        return self.__render()
        
    def account_form(self, plist, user='', pwd='', prot=''):
        self.__load_layout('account_form')
        
        protocols = self.protocols_for_options(plist, prot)
        self.app_layout = self.app_layout.replace('<% @user %>', user)
        self.app_layout = self.app_layout.replace('<% @pwd %>', pwd)
        self.app_layout = self.app_layout.replace('<% @protocols %>', protocols)
        return self.__render()
    
    def protocols_for_options(self, plist, default=''):
        ''' Receive an array of protocols like ['protocol1', 'protocol2'] '''
        protocols = '<option value="null">%s</option>' % i18n.get('--select--')
        for p in plist:
            checked = ''
            if p == default:
                checked = 'checked="checked"'
            protocols += '<option value="%s" %s>%s</option>' % (p, checked, p.capitalize())
        return protocols
    '''
    def accounts_for_options(self, alist, default=''):
        accounts = '<option value="null">%s</option>' % i18n.get('--account--')
        for a in alist:
            checked = ''
            if a.id_ == default:
                checked = 'selected="selected"'
            name = "%s (%s)" % (a.id_.split('-')[0], a.id_.split('-')[1])
            accounts += '<option value="%s" %s>%s</option>' % (a.id_, checked, name)
        return accounts
    
    def columns_for_options(self, clist, default=''):
        columns = '<option value="null">%s</option>' % i18n.get('--column--')
        for c in clist:
            checked = ''
            if c == default:
                checked = 'selected="selected"'
            columns += '<option value="%s" %s>%s</option>' % (c, checked, c)
        return columns
    '''
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
    
    def render_statuses(self, statuses):
        result = ''
        partial = self.__open_partial('status')
        for status in statuses:
            timestamp = status.datetime
            if status.source: 
                timestamp += ' %s %s' % (i18n.get('from'), status.source)
            if status.in_reply_to_user:
                timestamp += ' %s %s' % (i18n.get('in_reply_to'), status.in_reply_to_user)
            
            reposted_by = ''
            if status.reposted_by:
                count = len(status.reposted_by)
                if count > 1:
                    temp = '%i %s' % (count, i18n.get('people'))
                elif count == 1:
                    temp = '1 %s' % i18n.get('person')
                reposted_by = '%s %s' % (i18n.get('retweeted_by'), status.reposted_by)

            message = self.__highlight_urls(status, status.text)
            message = self.__highlight_hashtags(status, message)
            message = self.__highlight_groups(status, message)
            message = self.__highlight_mentions(status, message)
            username = self.__highlight_username(status)
            
            section = partial.replace('<% @status_id %>', status.id_)
            section = section.replace('<% @avatar %>', status.avatar)
            section = section.replace('<% @username %>', username)
            section = section.replace('<% @message %>', message)
            section = section.replace('<% @timestamp %>', timestamp)
            section = section.replace('<% @reposted_by %>', reposted_by)
            section = section.replace('<% @verified %>', self.__verified_tag(status.is_verified))
            section = section.replace('<% @protected %>', self.__protected_tag(status.is_protected))
            section = section.replace('<% @reposted %>', self.__reposted_tag(status.reposted_by))
            section = section.replace('<% @favorite %>', self.__favorite_tag(status.is_favorite, status.id_))
            
            result += section + '\n'
        
        page = self.__parse_tags(result)
        return page
    
    def render_column(self, column):
        protocol_img = column.protocol_id + '.png'
        label = "%s :: %s" % (column.account_id.split('-')[0], column.column_name)
        
        col_content = self.__open_partial('column_content')
        col_content = col_content.replace('<% @column_id %>', column.id_)
        col_content = col_content.replace('<% @column_label %>', label)
        col_content = col_content.replace('@protocol_img', protocol_img)
        
        col = self.__open_partial('column')
        col = col.replace('<% @column_id %>', column.id_)
        col = col.replace('<% @column_content %>', col_content)
        page = self.__parse_tags(col)
        return page
        

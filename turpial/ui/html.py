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
    
    def __favorite_tag(self, favorite, status_id):
        if favorite:
            cmd = "cmd:unfav:%s" % status_id
            icon = self.__image_tag("mark-favorite.png", 16, 16, class_='star')
        else:
            cmd = "cmd:fav:%s" % status_id
            icon = self.__image_tag("mark-unfavorite.png", 16, 16, class_='star')
        
        return "<a href='%s'>%s</a>" % (cmd, icon)
    
    def __highlight_hashtags(self, status, text):
        for h in status.entities['hashtags']:
            cad = '<a href="cmd:show_hashtag:%s">%s</a>' % (h, h)
            text = text.replace(h, cad)
        return text
    
    def __highlight_groups(self, status, text):
        for h in status.entities['groups']:
            cad = '<a href="cmd:show_group:%s">%s</a>' % (h, h)
            text = text.replace(h, cad)
        return text
    
    def __highlight_mentions(self, status, text):
        for h in status.entities['mentions']:
            #if len(h) == 1: 
            #    continue
            cad = '<a href="cmd:show_profile:%s">%s</a>' % (h, h)
            text = text.replace(h, cad)
        return text
        
    def __highlight_urls(self, status, text):
        for url in status.entities['url']:
            cad = '<a href="link:%s">%s</a>' % (url, url)
            text = text.replace(url, cad)
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
            args = command.split(':')[1].split('-%&%-')
        except IndexError:
            args = []
        return action, args
    
    def main(self, accounts, columns):
        self.__load_layout('main')
        empty = True
        for column in columns:
            if column: 
                empty = False
                break
        
        if empty:
            dock = ''
            content = self.__open_partial('empty')
        else:
            content = ''
            dock = self.__open_partial('dock')
            for column in columns:
                if not column: continue
                protocol_img = column.protocol_id + '.png'
                label = "%s :: %s" % (column.account_id, column.column_id.capitalize())
                
                col_content = self.__open_partial('column_content')
                col_content = col_content.replace('<% @column_id %>', column.id_)
                col_content = col_content.replace('<% @column_label %>', label)
                col_content = col_content.replace('@protocol_img', protocol_img)
                
                col = self.__open_partial('column')
                col = col.replace('<% @column_id %>', column.id_)
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
    
    def accounts_for_options(self, alist, default=''):
        ''' Receive an array of accounts objects '''
        accounts = '<option value="null">%s</option>' % i18n.get('--account--')
        for a in alist:
            checked = ''
            if a.id_ == default:
                checked = 'selected="selected"'
            name = "%s (%s)" % (a.id_.split('-')[0], a.id_.split('-')[1])
            accounts += '<option value="%s" %s>%s</option>' % (a.id_, checked, name)
        return accounts
    
    def columns_for_options(self, clist, default=''):
        ''' Receive an array of strings '''
        columns = '<option value="null">%s</option>' % i18n.get('--column--')
        for c in clist:
            checked = ''
            if c == default:
                checked = 'selected="selected"'
            columns += '<option value="%s" %s>%s</option>' % (c, checked, c)
        return columns
    
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
            
            section = partial.replace('<% @status_id %>', status.id_)
            section = section.replace('<% @avatar %>', status.avatar)
            section = section.replace('<% @username %>', status.username)
            section = section.replace('<% @message %>', message)
            section = section.replace('<% @timestamp %>', timestamp)
            section = section.replace('<% @repost %>', reposted_by)
            section = section.replace('<% @verified %>', self.__verified_tag(status.is_verified))
            section = section.replace('<% @protected %>', self.__protected_tag(status.is_protected))
            section = section.replace('<% @favorite %>', self.__favorite_tag(status.is_favorite, status.id_))
            
            result += section + '\n'
        
        page = self.__parse_tags(result)
        return page
    
    def render_columns_list(self, accounts, reg_columns, all_columns):
        result = ''
        partial = self.__open_partial('column_form')
        for col in reg_columns:
            columns = all_columns[col.account_id]
            acc_options = self.accounts_for_options(accounts, col.account_id)
            col_options = self.columns_for_options(columns, col.column_id)
            section = partial.replace('<% @column_id %>', col.id_)
            section = section.replace('<% @accounts %>', acc_options)
            section = section.replace('<% @columns %>', col_options)
            
            result += section + '\n'
        page = self.__parse_tags(result)
        return page
    
    def render_new_column(self, accounts, col_count):
        section = self.__open_partial('column_form')
        acc_options = self.accounts_for_options(accounts)
        col_options = self.columns_for_options([])
        section = section.replace('<% @column_id %>', str(col_count + 1))
        section = section.replace('<% @accounts %>', acc_options)
        section = section.replace('<% @columns %>', col_options)
        section = self.__parse_tags(section)
        return section
    
    def columns(self, accounts, reg_columns, all_columns):
        self.__load_layout('columns')
        col_list = self.render_columns_list(accounts, reg_columns, all_columns)
        self.app_layout = self.app_layout.replace('<% @columns %>', col_list)
        columns_js = self.js_columns_array(all_columns)
        accounts_js = self.js_accounts_array(accounts)
        script = '<script>' + columns_js + accounts_js + self.empty_column_label() + '</script>'
        self.app_layout = self.app_layout.replace('<% @variables_js %>', script)
        return self.__render()
    
    def empty_columns(self):
        self.__load_layout('columns')
        self.app_layout = self.app_layout.replace('<% @columns %>', i18n.get('no_column_yet'))
        script = '<script>$("#cmd_save").hide(); $("#cmd_new").hide();</script>'
        self.app_layout = self.app_layout.replace('<% @variables_js %>', script)
        return self.__render()
    
    def js_accounts_array(self, all_accounts):
        script = 'all_accounts = new Array;\n'
        array = "["
        for acc in all_accounts:
            array += "'%s'," % str(acc.id_)
        array = array[:-1] + "]"
        script += "all_accounts = %s;\n" % array
        return script
        
    def js_columns_array(self, all_columns):
        script = 'all_columns = new Object;\n'
        for key, value in all_columns.iteritems():
            array = "["
            for v in value:
                array += "'%s'," % str(v)
            array = array[:-1] + "]"
            script += "all_columns['%s'] = %s;\n" % (key, array)
        return script
    
    def empty_column_label(self):
        return 'empty_column_label = "%s";\n' % i18n.get('--column--')

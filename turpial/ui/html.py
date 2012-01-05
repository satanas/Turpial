# -*- coding: utf-8 -*-

# Webkit container for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 05, 2011

import re
import os
import urllib

from turpial.ui.lang import i18n
from libturpial.common import ARG_SEP, LoginStatus

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
        
        for js in ['jquery', 'jquery.autocomplete', 'common']:
            filepath = os.path.realpath(os.path.join(JS_LAYOUT_DIR, js + '.js'))
            self.scripts.append(filepath)
        
        # Load default css
        for css in ['common', 'jquery.autocomplete']:
            filepath = os.path.realpath(os.path.join(CSS_LAYOUT_DIR, css + '.css'))
            self.styles.append(filepath)
        
        js_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'js', res + '.js'))
        if os.path.isfile(js_file):
            self.scripts.append(js_file)
        
        css_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'css', res + '.css'))
        if os.path.isfile(css_file):
            self.styles.append(css_file)
        
    def __image_tag(self, filename, base=True, width=None, height=None, class_=None, visible=True):
        if base:
            filepath = os.path.realpath(os.path.join(IMAGES_DIR, filename))
        else:
            filepath = os.path.realpath(os.path.join(DEFAULT_IMAGES_DIR, filename))
        
        class_tag = ''
        if class_:
            class_tag = "class='%s'" % class_
        
        visible_tag = ''
        if not visible:
            visible_tag = "style='display: none;'"
        
        if width and height:
            return "<img src='file://%s' width='%s' height='%s' %s %s/>" % (filepath, width, height, class_tag, visible_tag)
        else:
            return "<img src='file://%s' %s %s/>" % (filepath, class_tag, visible_tag)
    
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
            return self.__image_tag("mark-repeated.png", 16, 16, class_='repost_mark')
        else:
            return ''
    
    def __favorite_tag(self):
        return self.__image_tag("mark-favorite.png", 16, 16, class_='star')
 
    def __retweeted_tag(self):
        return self.__image_tag("mark-retweeted.png", 16, 16, class_='retweeted')
   
    def __retweeted_visible(self, status):
        if status.retweeted:
            return 'display: block;'
        return 'display: none;'

    def __favorite_visible(self, status):
        if status.is_favorite:
            return 'display: block;'
        return 'display: none;'
    
    def __login_action_tag(self, account):
        if account.logged_in == LoginStatus.NONE:
            return "<a href='cmd:login:%s'>%s</a>" % (account.id_, i18n.get('login'))
        elif account.logged_in == LoginStatus.IN_PROGRESS:
            return "<span class=\"progress\">%s</span>" % (i18n.get('in_progress'))
        elif account.logged_in == LoginStatus.DONE:
            return "<span class=\"done\">%s</span>" % (i18n.get('logged_in'))
            
    def __highlight_username(self, status):
        args = "'%s', '%s'" % (status.account_id, status.username)
        return '<a href="javascript: show_profile_window(%s);">%s</a>' % (args, status.username)

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
            args = "'%s', '%s'" % (status.account_id, h.display_text[1:])
            cad = '<a href="javascript: show_profile_window(%s);">%s</a>' % (args, h.display_text)
            pattern = re.compile(h.search_for, re.IGNORECASE)
            text = pattern.sub(cad, text)
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
    
    def __build_status_menu(self, status):
        menu = ''
        if not status.is_own:
            # Reply
            mentions = status.get_reply_mentions()
            str_mentions = '[\'' + '\',\''.join(mentions) + '\']'
            title = i18n.get('in_reply_to').capitalize() + " " + mentions[0]
            cmd = "'%s','%s','%s',%s" % (status.account_id, status.id_, title, str_mentions)
            menu += "<a href=\"javascript: reply_status(%s)\" class='action'>%s</a>" % (cmd, i18n.get('reply'))
            
            # Quote
            cmd = "'%s','%s','%s'" % (status.account_id, status.username, urllib.quote(status.text.encode('utf-8')))
            menu += "<a href=\"javascript: quote_status(%s)\" class='action'>%s</a>" % (cmd, i18n.get('quote'))
            
            # Repeat
            cmd = ARG_SEP.join([status.account_id, status.id_])
            if status.retweeted:
                menu += "<a id='repeat-mark-%s' href='cmd:unrepeat_status:%s' class='action'>%s</a>" % (status.id_, cmd, i18n.get('-retweet'))
            else:
                menu += "<a id='repeat-mark-%s' href='cmd:repeat_status:%s' class='action'>%s</a>" % (status.id_, cmd, i18n.get('+retweet'))
            
            # Fav
            args = ARG_SEP.join([status.account_id, status.id_])
            if status.is_favorite:
                cmd = "cmd:unfav_status:%s" % args
                menu += "<a id='fav-mark-%s' href='%s' class='action'>%s</a>" % (status.id_, cmd, i18n.get('-fav'))
            else:
                cmd = "cmd:fav_status:%s" % args
                menu += "<a id='fav-mark-%s' href='%s' class='action'>%s</a>" % (status.id_, cmd, i18n.get('+fav'))
        else:
            cmd = ARG_SEP.join([status.account_id, status.id_])
            menu += "<a href='cmd:delete_status:%s' class='action'>%s</a>" % (cmd, i18n.get('delete'))
        return menu
    
    def __build_profile_menu(self, profile):
        if profile.is_me():
            return "<span class='disabled action'>%s</span>" % (i18n.get('this_is_you'))
        
        menu = ''
        cmd = ARG_SEP.join([profile.account_id, profile.username])
        # Direct Messages
        menu += "<a href=\"%s\" class='action'>%s</a>" % (cmd, i18n.get('message'))
        
        # Follow
        if profile.following:
            menu += "<a id='profile-follow-cmd' href='cmd:unfollow:%s' class='action'>%s</a>" % (cmd, i18n.get('unfollow'))
        elif profile.follow_request:
            menu += "<span class='action'>%s</span>" % (i18n.get('requested'))
        else:
            menu += "<a id='profile-follow-cmd' href='cmd:follow:%s' class='action'>%s</a>" % (cmd, i18n.get('follow'))
        
        # Mute
        if profile.muted:
            menu += "<a id='profile-mute-cmd' href='cmd:unmute:%s' class='action'>%s</a>" % (profile.username, i18n.get('unmute'))
        else:
            menu += "<a id='profile-mute-cmd' href='cmd:mute:%s' class='action'>%s</a>" % (profile.username, i18n.get('mute'))
        
        # Block
        menu += "<a href='cmd:block:%s' class='action'>%s</a>" % (cmd, i18n.get('block'))
        
        # Spam
        menu += "<a href='cmd:report_spam:%s' class='action'>%s</a>" % (cmd, i18n.get('spam'))
        
        return menu
            
    def __account_buttons(self, accounts):
        buttons = ''
        for acc in accounts:
            name = acc.split('-')[0]
            image_name = acc.split('-')[1] + ".png"
            image = self.__image_tag(image_name, 16, 16)
            #buttons += "<a href='#' title='%s' class='toggle'>%s</a>" % (name, image)
            buttons += "<div class='checkbox' title='%s'>%s<label><input id='acc-selector-%s' type='checkbox' class='acc_selector' value='%s' /></label><div class='clearfix'></div></div>" % (name, image, acc, acc)
        return buttons
        
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
    
    def js_string_array(self, array):
        return '["' + '","'.join(array) + '"]'
        
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
        acc_buttons = self.__account_buttons(accounts)
        self.app_layout = self.app_layout.replace('<% @content %>', content)
        self.app_layout = self.app_layout.replace('<% @account_buttons %>', acc_buttons)
        
        page = self.__render()
        # TODO: Look for a better way of handle javascript code from python
        page = page.replace('<% @arg_sep %>', ARG_SEP)
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
    
    def render_account_list(self, accounts):
        self.partials['accounts'] = ''
        partial = self.__open_partial('account')
        for acc in accounts:
            section = partial.replace('<% @account_id %>', acc.id_)
            section = section.replace('<% @account_name %>', acc.profile.username)
            section = section.replace('<% @protocol_id %>', acc.id_.split('-')[1])
            section = section.replace('@protocol_img', acc.id_.split('-')[1] + '.png')
            section = section.replace('<% @login_action %>', self.__login_action_tag(acc))
            
            self.partials['accounts'] += section + '\n'
        page = self.__parse_tags(self.partials['accounts'])
        
        return page
    
    def statuses(self, statuses):
        result = ''
        for status in statuses:
            result += self.status(status) + '\n'
        page = self.__parse_tags(result)
        return page
    
    def single_status(self, status):
        result = self.status(status)
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
    
    def status(self, status, ignore_reply=False):
        timestamp = status.datetime
        if status.source: 
            if status.source.url:
                timestamp += ' %s <a href="link:%s">%s</a>' % (i18n.get('from'), status.source.url, status.source.name)
            else:
                timestamp += ' %s %s' % (i18n.get('from'), status.source.name)
        
        if status.in_reply_to_user and not ignore_reply:
            args = ARG_SEP.join([status.account_id, status.id_, '%s' % status.in_reply_to_id])
            timestamp += ' <a href="cmd:showreply:%s">%s %s</a>' % (args, i18n.get('in_reply_to'), status.in_reply_to_user)
            timestamp += ' <a href="cmd:showconversation:%s">(%s)</a>' % (args, i18n.get('show_all'))
        
        reposted_by = ''
        if status.reposted_by:
            count = len(status.reposted_by)
            if count > 1:
                temp = '%i %s' % (count, i18n.get('people'))
            elif count == 1:
                temp = '1 %s' % i18n.get('person')
            reposted_by = '%s %s' % (i18n.get('retweeted_by'), status.reposted_by)
        if status.text.find('\\') > 0:
            print status.text
        message = self.__highlight_urls(status, status.text)
        message = self.__highlight_hashtags(status, message)
        message = self.__highlight_groups(status, message)
        message = self.__highlight_mentions(status, message)
        message = message.replace('\r', ' ')
        message = message.replace('\\"', '"')
        message = message.replace('\\', "&#92;")
        username = self.__highlight_username(status)
        menu = self.__build_status_menu(status)

        args = ARG_SEP.join([status.account_id, status.id_])
        
        
        section = self.__open_partial('status')
        section = section.replace('<% @status_id %>', status.id_)
        if status.in_reply_to_id:
            section = section.replace('<% @status_replyto_id %>', '%s' % status.id_)
            
        section = section.replace('<% @avatar %>', status.avatar)
        section = section.replace('<% @username %>', username)
        section = section.replace('<% @message %>', message)
        section = section.replace('<% @timestamp %>', timestamp)
        section = section.replace('<% @reposted_by %>', reposted_by)
        section = section.replace('<% @verified %>', self.__verified_tag(status.is_verified))
        section = section.replace('<% @protected %>', self.__protected_tag(status.is_protected))
        section = section.replace('<% @reposted %>', self.__reposted_tag(status.reposted_by))
        section = section.replace('<% @fav_visible %>', self.__favorite_visible(status))
        section = section.replace('<% @favorite %>', self.__favorite_tag())
        section = section.replace('<% @retweeted_visible %>', self.__retweeted_visible(status))
        section = section.replace('<% @retweeted %>', self.__retweeted_tag())
        section = section.replace('<% @menu %>', menu)

        return section      
    
    def profile(self, profile):
        bio_icon = self.__image_tag('icon-bio.png', width='16', height='16', class_='mark')
        loc_icon = self.__image_tag('icon-location.png', width='16', height='16', class_='mark')
        web_icon = self.__image_tag('icon-web.png', width='16', height='16', class_='mark')
        url = ''
        if profile.url != '' and profile.url != None:
            url = '<a href="link:%s">%s</a>' % (profile.url, profile.url)
        bio = ''
        if profile.bio:
            bio = profile.bio
        location = ''
        if profile.location:
            location = profile.location
        section = self.__open_partial('profile')
        section = section.replace('<% @avatar %>', profile.avatar)
        section = section.replace('<% @fullname %>', profile.fullname)
        section = section.replace('<% @username %>', profile.username)
        section = section.replace('<% @verified %>', self.__verified_tag(profile.verified))
        section = section.replace('<% @protected %>', self.__protected_tag(profile.protected))
        section = section.replace('<% @bio_icon %>', bio_icon)
        section = section.replace('<% @location_icon %>', loc_icon)
        section = section.replace('<% @web_icon %>', web_icon)
        section = section.replace('<% @bio %>', bio)
        section = section.replace('<% @location %>', location)
        section = section.replace('<% @web %>', url)
        section = section.replace('<% @following %>', str(profile.friends_count))
        section = section.replace('<% @followers %>', str(profile.followers_count))
        section = section.replace('<% @posts %>', str(profile.statuses_count))
        section = section.replace('<% @favorites %>', str(profile.favorites_count))
        section = section.replace('<% @menu %>', self.__build_profile_menu(profile))
        page = self.__parse_tags(section)
        print page
        return page

# -*- coding: utf-8 -*-

# Webkit container for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Oct 05, 2011

import re
import os
import sys
import urllib

from turpial import VERSION
from turpial.ui.lang import i18n
from libturpial.common import ARG_SEP, LoginStatus
from libturpial.api.services.showmedia import utils as showmediautils

#pyinstaller compatibility validation
if getattr(sys, 'frozen', None):
    DATA_DIR = os.path.realpath(os.path.join(sys._MEIPASS))
else:
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
    def __init__(self,*args):
        self.scripts = []
        self.scripts_impress = []
        self.styles = []
        self.styles_impress = []
        self.partials = {}

    def __url_quote(self, text):
        ntext = text.encode('utf-8').replace('\\\\', '\\')
        return urllib.quote(ntext)

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
        self.scripts_impress = []
        self.styles = []
        self.styles_impress = []
        self.partials = {}

        self.app_layout = self.__open_template(res)

        # Load default js

        for js in ['jquery', 'jquery.hotkeys', 'jquery.autocomplete', 'common']:
            filepath = os.path.realpath(os.path.join(JS_LAYOUT_DIR, js + '.js'))
            self.scripts.append(filepath)

        for js in ['animation', 'fx-m']:
            filepath = os.path.realpath(os.path.join(JS_LAYOUT_DIR, js + '.js'))
            self.scripts_impress.append(filepath)

        # Load default css
        for css in ['common', 'jquery.autocomplete', 'grids-min']:
            filepath = os.path.realpath(os.path.join(CSS_LAYOUT_DIR, css + '.css'))
            self.styles.append(filepath)

        # Load default css_impress
        for css in ['general', 'index']:
            filepath = os.path.realpath(os.path.join(CSS_LAYOUT_DIR, css + '.css'))
            self.styles_impress.append(filepath)

        js_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'js', res + '.js'))
        if os.path.isfile(js_file):
            self.scripts.append(js_file)

        css_file = os.path.realpath(os.path.join(LAYOUT_DIR, 'css', res + '.css'))
        if os.path.isfile(css_file):
            self.styles.append(css_file)

    def __image_tag(self, filename, base=True, width=None, height=None, class_=None, visible=True, tooltip=''):
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

        tooltip_tag = ''
        if tooltip:
            tooltip_tag = """ title="%s" alt="%s" """ % (tooltip, tooltip)

        if width and height:
            return "<img src='file://%s' width='%s' height='%s' %s %s %s/>" % (filepath, width, height, class_tag, visible_tag, tooltip_tag)
        else:
            return "<img src='file://%s' %s %s %s/>" % (filepath, class_tag, visible_tag, tooltip_tag)

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

    def __favorite_tag(self, favorite):
        if favorite:
            return self.__image_tag("action-fav.png", 16, 16, class_='star')
        else:
            return self.__image_tag("action-unfav.png", 16, 16, class_='star')

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
            #if url.url[0:7] != "http://":
            #    url.url = "http://%s" % url.url
            if not showmediautils.is_service_supported(url.url):
                cad = '<a href="link:%s" title="%s">%s</a>' % (url.url, url.url,
                    url.display_text)
            else:
                pars = ARG_SEP.join([url.url.replace(":", "$"), status.account_id])
                cad = '<a href="cmd:show_media:%s" title="%s">%s</a>' % (pars, url.url,
                    url.display_text)
            text = text.replace(url.search_for, cad)
        return text

    def __build_status_menu(self, status):
        menu = ''
        if not status.is_own and not status.is_direct():
            # Reply
            mentions = status.get_reply_mentions()
            str_mentions = '[\'' + '\',\''.join(mentions) + '\']'
            title = i18n.get('in_reply_to').capitalize() + " " + mentions[0]
            cmd = "'%s','%s','%s',%s" % (status.account_id, status.id_, title, str_mentions)
            menu += "<a href=\"javascript: reply_status(%s)\" class='action'>%s</a>" % (cmd, self.__image_tag('action-reply.png',
                tooltip=i18n.get('reply')))

            # Repeat
            args = ARG_SEP.join([status.account_id, status.id_, status.username, self.__url_quote(status.text)])
            menu += "<a href='cmd:repeat_menu:%s' class='action'>%s</a>" % (args, self.__image_tag('action-repeat.png',
                tooltip=i18n.get('repeat')))

            # Conversation
            if status.in_reply_to_user:
                args = ARG_SEP.join([status.account_id, status.id_, '%s' % status.in_reply_to_id])
                menu += """<a href='cmd:show_conversation:%s' class='action'>%s</a>""" % (args, self.__image_tag('action-conversation.png',
                    tooltip=i18n.get('conversation')))

        elif not status.is_own and status.is_direct():
            # Reply
            cmd = "'%s','%s'" % (status.account_id, status.username)
            menu += "<a href=\"javascript: reply_direct(%s)\" class='action'>%s</a>" % (cmd, self.__image_tag('action-reply.png',
                tooltip=i18n.get('reply')))

            # Delete
            cmd = ARG_SEP.join([status.account_id, status.id_])
            menu += """<a href="javascript:show_confirm_window('%s', '%s', 'cmd:delete_direct:%s')" class='action'>%s</a>""" % (
                    i18n.get('confirm_delete'), i18n.get('do_you_want_to_delete_direct_message'), cmd, self.__image_tag('action-delete.png',
                    tooltip=i18n.get('delete')))
        elif status.is_own and not status.is_direct():
            cmd = ARG_SEP.join([status.account_id, status.id_])
            menu += """<a href="javascript:show_confirm_window('%s', '%s', 'cmd:delete_status:%s')" class='action'>%s</a>""" % (
                    i18n.get('confirm_delete'), i18n.get('do_you_want_to_delete_status'), cmd, self.__image_tag('action-clear.png',
                    tooltip=i18n.get('delete')))
        elif status.is_own and status.is_direct():
            cmd = ARG_SEP.join([status.account_id, status.id_])
            menu += """<a href="javascript:show_confirm_window('%s', '%s', 'cmd:delete_direct:%s')" class='action'>%s</a>""" % (
                    i18n.get('confirm_delete'), i18n.get('do_you_want_to_delete_direct_message'), cmd, self.__image_tag('action-clear.png',
                    tooltip=i18n.get('delete')))
        return menu

    def __build_profile_menu(self, profile):
        if profile.is_me():
            return "<span class='disabled action_you'>%s</span>" % (i18n.get('this_is_you'))

        menu = ''
        cmd = "'%s','%s'" % (profile.account_id, profile.username)
        # Direct Messages
        menu += "<a href=\"javascript: send_direct_from_profile(%s)\" class='action'>%s</a>" % (cmd, i18n.get('message'))

        # Follow
        cmd = ARG_SEP.join([profile.account_id, profile.username])
        if profile.following:
            label = i18n.get('do_you_want_to_unfollow_user') % profile.username
            menu += """<a id='profile-follow-cmd' href="javascript:show_confirm_window('%s', '%s', 'cmd:unfollow:%s')" class='action'>%s</a>""" % (
                    i18n.get('confirm_unfollow'), label, cmd, i18n.get('unfollow'))
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
            buttons += "<div class='checkbox' title='%s'>%s<label><span>%s</span><input id='acc-selector-%s' type='checkbox' class='acc_selector' value='%s' style='vertial-align:middle;' /></label><div class='clearfix'></div></div>" % (name, image, name, acc, acc)
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

    def __render(self, tofile=True):
        page = self.app_layout

        js_tags = '<script type="text/javascript">'
        for js in self.scripts:
            fd = open(js, 'r')
            resource = fd.read()
            fd.close()
            js_tags += resource + '\n'
        js_tags += '</script>'
        page = page.replace('<% javascripts %>', js_tags)

        js_tags = '<script type="text/javascript">'
        for js in self.scripts_impress:
            fd = open(js, 'r')
            resource = fd.read()
            fd.close()
            js_tags += resource + '\n'
        js_tags += '</script>'
        page = page.replace('<% javascripts_impress %>', js_tags)

        css_tags = '<style type="text/css">'
        for css in self.styles:
            fd = open(css, 'r')
            resource = fd.read()
            fd.close()
            css_tags += resource + '\n'
        css_tags += '</style>'
        page = page.replace('<% stylesheets %>', css_tags)

        css_tags = '<style type="text/css">'
        for css in self.styles_impress:
            fd = open(css, 'r')
            resource = fd.read()
            fd.close()
            css_tags += resource + '\n'
        css_tags += '</style>'

        page = page.replace('<% stylesheets_impress %>', css_tags)

        page = page.replace('<% query %>', self.__query_tag())

        page = self.__parse_tags(page)
        if tofile:
            fd = open('/tmp/output.html', 'w')
            fd.write(page)
            fd.close()
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
        hdr_content = ''
        col_content = ''
        for column in columns:
            hdr, col = self.render_column(column)
            hdr_content += hdr
            col_content += col
        acc_buttons = self.__account_buttons(accounts)
        self.app_layout = self.app_layout.replace('<% @headers %>', hdr_content)
        self.app_layout = self.app_layout.replace('<% @columns %>', col_content)
        self.app_layout = self.app_layout.replace('<% @account_buttons %>', acc_buttons)

        page = self.__render(tofile=False)
        # TODO: Look for a better way of handle javascript code from python
        page = page.replace('<% @arg_sep %>', ARG_SEP)
        page = page.replace('<% @num_columns %>', str(len(columns)))

        fd = open('/tmp/output.html', 'w')
        fd.write(page)
        fd.close()
        return page

    def accounts(self, accounts):
        self.__load_layout('accounts')
        acc_list = self.render_account_list(accounts)
        self.app_layout = self.app_layout.replace('<% @accounts %>', acc_list)
        return self.__render()

    def about(self):
        self.__load_layout('about2')
        self.app_layout = self.app_layout.replace('<% VERSION  %>', VERSION)
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
        label = ''
        if column.column_name == 'public':
            label = "%s :: %s" % (column.column_name, i18n.get('timeline'))
        else:
            label = "%s :: %s" % (column.account_id.split('-')[0], column.column_name)

        col_header = self.__open_partial('column_header')
        col_header = col_header.replace('<% @column_label %>', label)
        col_header = col_header.replace('<% @column_id %>', column.id_)
        col_header = col_header.replace('@protocol_img', protocol_img)

        col_content = self.__open_partial('column_content')
        col_content = col_content.replace('<% @column_id %>', column.id_)

        header = self.__parse_tags(col_header)
        column = self.__parse_tags(col_content)
        return header, column

    def status(self, status, ignore_reply=False, profile_status=False):
        timestamp = status.datetime
        if status.source:
            if status.source.url:
                timestamp += ' %s <a href="link:%s">%s</a>' % (i18n.get('from'), status.source.url, status.source.name)
            else:
                timestamp += ' %s %s' % (i18n.get('from'), status.source.name)

        if status.in_reply_to_user and not ignore_reply:
            timestamp += ' %s %s' % (i18n.get('in_reply_to'), status.in_reply_to_user)

        reposted_by = ''
        if status.reposted_by:
            count = len(status.reposted_by)
            if count > 1:
                temp = '%i %s' % (count, i18n.get('people'))
            elif count == 1:
                temp = '1 %s' % i18n.get('person')
            reposted_by = '%s %s' % (i18n.get('retweeted_by'), status.reposted_by)

        args = ARG_SEP.join([status.account_id, status.id_])
        tmp_cmd = "<a name='fav-cmd' href='%s' class='action'>%s</a>"
        if status.is_favorite:
            cmd = "cmd:unfav_status:%s" % args
            fav_cmd = tmp_cmd % (cmd, self.__image_tag('action-fav.png', tooltip=i18n.get('-fav')))
            is_fav = 'true'
            show_fav = ''
        else:
            cmd = "cmd:fav_status:%s" % args
            fav_cmd = tmp_cmd % (cmd, self.__image_tag('action-unfav.png', tooltip=i18n.get('+fav')))
            is_fav = 'false'
            show_fav = 'display: none'

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

        # Decide what template to use
        if profile_status:
            section = self.__open_partial('profile_status')
        else:
            section = self.__open_partial('status')

        section = section.replace('<% @status_id %>', status.id_)
        section = section.replace('<% @status_display_id %>', status.display_id)
        if status.in_reply_to_id:
            section = section.replace('<% @status_replyto_id %>', '%s' % status.id_)
        else:
            section = section.replace('<% @status_replyto_id %>', '')

        section = section.replace('<% @avatar %>', status.avatar)
        section = section.replace('<% @account_id %>', status.account_id)
        section = section.replace('<% @clean_username %>', status.username)
        section = section.replace('<% @username %>', username)
        section = section.replace('<% @message %>', message)
        section = section.replace('<% @timestamp %>', timestamp)
        section = section.replace('<% @reposted_by %>', reposted_by)
        section = section.replace('<% @verified %>', self.__verified_tag(status.is_verified))
        section = section.replace('<% @protected %>', self.__protected_tag(status.is_protected))
        section = section.replace('<% @reposted %>', self.__reposted_tag(status.reposted_by))
        section = section.replace('<% @is_fav %>', is_fav)
        section = section.replace('<% @show_favorite %>', show_fav)
        section = section.replace('<% @favorite_cmd %>', fav_cmd)
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
        section = section.replace('<% @account_id %>', profile.account_id)
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
        recent = ''
        for status in profile.recent_updates:
            recent += self.status(status, profile_status=True)
        section = section.replace('<% @recent_updates %>', recent)
        page = self.__parse_tags(section)
        #print page
        return page

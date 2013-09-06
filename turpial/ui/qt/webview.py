# -*- coding: utf-8 -*-

# Qt widget to show statusesin Turpial using a QWebView

import os

from jinja2 import Template

from PyQt4.QtWebKit import QWebView
from PyQt4.QtWebKit import QWebPage
from PyQt4.QtWebKit import QWebSettings

from PyQt4.QtCore import pyqtSignal

from turpial.ui.lang import i18n

class StatusesWebView(QWebView):

    link_clicked = pyqtSignal(str)
    hashtag_clicked = pyqtSignal(str)
    profile_clicked = pyqtSignal(str)
    cmd_clicked = pyqtSignal(str)

    def __init__(self, base, column_id):
        QWebView.__init__(self)
        self.base = base
        self.column_id = column_id
        self.linkClicked.connect(self.__element_clicked)
        page = self.page()
        page.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.setPage(page)
        self.status_template = self.__load_template('status.html')

        self.stylesheet = self.__load_stylesheet()
        self.show()

    def __element_clicked(self, qurl):
        url = str(qurl.toString())
        if url.startswith('http'):
            self.link_clicked.emit(url)
        elif url.startswith('hashtag'):
            hashtag = "#%s" % url.split(':')[2]
            self.hashtag_clicked.emit(hashtag)
        elif url.startswith('profile'):
            self.profile_clicked.emit(url.split(':')[1])
        elif url.startswith('cmd'):
            self.cmd_clicked.emit(url.split('cmd:')[1])

    def __load_template(self, name):
        path = os.path.join(self.base.templates_path, name)
        fd = open(path)
        content = fd.read()
        fd.close()
        return Template(content)

    def __load_stylesheet(self):
        attrs = {
            'mark_protected': os.path.join(self.base.images_path, 'mark-protected.png'),
            'mark_favorited': os.path.join(self.base.images_path, 'mark-favorited2.png'),
            'mark_repeated': os.path.join(self.base.images_path, 'mark-repeated2.png'),
            'mark_reposted': os.path.join(self.base.images_path, 'mark-reposted.png'),
            'mark_verified': os.path.join(self.base.images_path, 'mark-verified.png'),
            'action_reply': os.path.join(self.base.images_path, 'action-reply.png'),
            'action_repeat': os.path.join(self.base.images_path, 'action-repeat.png'),
            'action_quote': os.path.join(self.base.images_path, 'action-quote.png'),
            'action_favorite': os.path.join(self.base.images_path, 'action-favorite.png'),
            'action_reply_shadowed': os.path.join(self.base.images_path, 'action-reply-shadowed.png'),
            'action_repeat_shadowed': os.path.join(self.base.images_path, 'action-repeat-shadowed.png'),
            'action_quote_shadowed': os.path.join(self.base.images_path, 'action-quote-shadowed.png'),
            'action_favorite_shadowed': os.path.join(self.base.images_path, 'action-favorite-shadowed.png'),
            'action_delete': os.path.join(self.base.images_path, 'action-delete.png'),
            'action_delete_shadowed': os.path.join(self.base.images_path, 'action-delete-shadowed.png'),
        }
        stylesheet = self.__load_template('style.css')
        return stylesheet.render(attrs)

    def __render_status(self, status, with_conversation=True):
        repeated_by = None
        conversation_id = None
        view_conversation = None
        message = status.text
        timestamp = self.base.humanize_timestamp(status.timestamp)

        if status.entities:
            # Highlight URLs
            for url in status.entities['urls']:
                pretty_url = "<a href='%s'>%s</a>" % (url.url, url.display_text)
                message = message.replace(url.search_for, pretty_url)
            # Highlight hashtags
            for hashtag in status.entities['hashtags']:
                pretty_hashtag = "<a href='hashtag:%s:%s'>%s</a>" % (hashtag.account_id,
                        hashtag.display_text[1:], hashtag.display_text)
                message = message.replace(hashtag.search_for, pretty_hashtag)
            # Highlight mentions
            for mention in status.entities['mentions']:
                pretty_mention = "<a href='profile:%s'>%s</a>" % (mention.url, mention.display_text)
                message = message.replace(mention.search_for, pretty_mention)

        if status.repeated_by:
            repeated_by = "%s %s" % (i18n.get('retweeted_by'), status.repeated_by)
        if status.in_reply_to_id and with_conversation:
            conversation_id = "%s-conversation-%s" % (self.column_id, status.id_)
            view_conversation = i18n.get('view_conversation')

        attrs = {'status': status, 'message': message, 'repeated_by': repeated_by,
                'timestamp': timestamp, 'view_conversation': view_conversation, 'reply': i18n.get('reply'),
                'quote': i18n.get('quote'), 'retweet': i18n.get('retweet'),
                'mark_as_favorite': i18n.get('mark_as_favorite'), 'delete': i18n.get('delete'),
                'remove_from_favorites': i18n.get('remove_from_favorites'),
                'conversation_id': conversation_id}

        content = self.status_template.render(attrs)
        if conversation_id:
            content += "<div id='%s' class='conversation'></div>" % conversation_id
        return content


    def update_statuses(self, statuses):
        content = ''
        processed_statuses = {}

        for status in statuses:
            processed_statuses[status.id_] = status
            content += self.__render_status(status)

        column = self.__load_template('column.html')
        args = {'stylesheet': self.stylesheet, 'content': content,
            'favorite_tooltip': i18n.get('mark_as_favorite'),
            'unfavorite_tooltip': i18n.get('remove_from_favorites')}
        html = column.render(args)

        self.setHtml(html)
        return processed_statuses

    def execute_javascript(self, js_cmd):
        self.page().mainFrame().evaluateJavaScript(js_cmd)

    def update_conversation(self, status, conversation_id):
        status_rendered = self.__render_status(status, with_conversation=False)
        status_rendered = status_rendered.replace("\n", '')
        status_rendered = status_rendered.replace('\'', '"')
        conversation = """updateConversation('%s', '%s')""" % (conversation_id, status_rendered)
        self.execute_javascript(conversation)

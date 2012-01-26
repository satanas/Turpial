# -*- coding: utf-8 -*-

"""Funciones utilitarias comúnes a todas las vistas"""
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2009

import re
import time
import htmlentitydefs
import xml.sax.saxutils as saxutils

AVATAR_SIZE = 48

HASHTAG_PATTERN = re.compile('(?<![\w])#[\wáéíóúÁÉÍÓÚñÑçÇ]+')
GROUP_PATTERN = re.compile('(?<![\w])![\wáéíóúÁÉÍÓÚñÑçÇ]+')
MENTION_PATTERN = re.compile('(?<![\w])@[\w]+')
CLIENT_PATTERN = re.compile('<a href="(.*?)">(.*?)</a>')
# According to RFC 3986 - http://www.ietf.org/rfc/rfc3986.txt
URL_PATTERN = re.compile('((?<!\w)(http://|ftp://|https://|www\.)[-\w._~:/?#\[\]@!$&\'()*+,;=]*)')

def detect_client(tweet):
    '''Parse the source of a tweet'''
    if not tweet.source:
        return None
    text = saxutils.unescape(tweet.source)
    text = text.replace('&quot;', '"')
    if text == 'web':
        return text
    rtn = CLIENT_PATTERN.search(text)
    if rtn:
        return rtn.groups()[1]
    return tweet.source
    
def detect_hashtags(text):
    '''Returns an array with all hashtag in a tweet'''
    return HASHTAG_PATTERN.findall(text)
    
def detect_groups(text):
    '''Returns an array with all hashtag in a tweet'''
    return GROUP_PATTERN.findall(text)
    
def detect_mentions(text):
    '''Returns an array with all mentions in a tweet'''
    return MENTION_PATTERN.findall(text)
    
def detect_urls(text):
    '''Returns an array with all URLs in a tweet'''
    urls = []
    match_urls = URL_PATTERN.findall(text)
    for item in match_urls:
        url = item[0]
        # Elimina el último paréntesis en las expresiones regulares
        if url[-1] == ')':
            url = url[:-1]
        urls.append(url)
    return urls
    
def get_rates(resp):
    '''Returns the status bar message about API calls'''
    if resp.type == 'error':
        return resp.errmsg
    else:
        val = resp.items
        tsec = val.reset_time_in_seconds - time.timezone
        t = time.strftime('%I:%M %P', time.gmtime(tsec))
        hits = val.remaining_hits
        limit = val.hourly_limit
        return "%s %s %s %s: %s" % (hits, _('of'), limit, _('API calls. Reset'), t)
    
def has_tweet(src, tweet):
    '''Returns True if tweet is in src. False otherwise'''
    for t in src:
        if tweet.id == t.id:
            return True
    return False
    
#def escape_text(text):
#    '''Returns a text HTML escaped'''
#    return saxutils.escape(text)
    
def unescape_text(text):
    '''Removes HTML or XML character references and entities from a text 
    string'''
    text = saxutils.unescape(text)
    '''
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    
    return re.sub("&#?\w+;", fixup, text)
    '''
    text = text.replace('&quot;', '"')
    text = text.replace('\r\n', ' ')
    text = text.replace('\n', ' ')
    return text

def get_reply_all(user, me, text):
    ''' Devuelve una cadena con los nombres de todos los mencionados en un 
    estado y el número de menciones no repetidas (que no incluyan al
    mismo usuario) '''
    re_all = user
    count = 0
    mentions = detect_mentions(text)
    for h in mentions:
        if h[1:] == me:
            continue
        if re_all.find(h[1:]) > 0:
            continue
        count += 1
        re_all += '%s ' % h
    
    return re_all, count

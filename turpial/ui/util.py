# -*- coding: utf-8 -*-

"""Funciones utilitarias comúnes a todas las vistas"""
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2009

import re
import time
import datetime
import htmlentitydefs
import xml.sax.saxutils as saxutils

AVATAR_SIZE = 48

HASHTAG_PATTERN = re.compile('(?<![\w])#[\wáéíóúÁÉÍÓÚñÑçÇ]+')
GROUP_PATTERN = re.compile('(?<![\w])![\wáéíóúÁÉÍÓÚñÑçÇ]+')
MENTION_PATTERN = re.compile('(?<![\w])@[\w]+')
CLIENT_PATTERN = re.compile('<a href="(.*?)">(.*?)</a>')
URL_PATTERN = re.compile('((http|ftp|https)://[-A-Za-z0-9+&@#/%?=~_:.\[\]]*[-A-Za-z0-9+&@#/%?=~_:\[\]()])')

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
    temp = URL_PATTERN.findall(text)
    for u in temp:
        urls.append(u[0])
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

def get_timestamp(tweet):
    '''Returns the timestamp for a tweet'''
    # Tue Mar 13 00:12:41 +0000 2007 -> Tweets normales
    # Wed, 08 Apr 2009 19:22:10 +0000 -> Busquedas
    month_names = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
        'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    date_info = tweet.datetime.split()
    
    if date_info[1] in month_names:
        month = month_names.index(date_info[1])
        day = int(date_info[2])
        year = int(date_info[5])
        time_info = date_info[3].split(':')
    else:
        month = month_names.index(date_info[2])
        day = int(date_info[1])
        year = int(date_info[3])
        time_info = date_info[4].split(':')
        
    hour = int(time_info[0])
    minute = int(time_info[1])
    second = int(time_info[2])
    
    d = datetime.datetime(year, month, day, hour, minute, second)
    
    i_hate_timezones = time.timezone
    if (time.daylight):
        i_hate_timezones = time.altzone
    
    dt = datetime.datetime(*d.timetuple()[:-3]) - \
         datetime.timedelta(seconds=i_hate_timezones)
    t = dt.timetuple()
    
    return time.strftime('%b %d, %I:%M %p', t)

def count_new_tweets(tweets, last):
    '''Returns the number of new tweets in tweets'''
    if not last:
        return 0
    if (tweets is None) or (len(tweets) <= 0):
        return 0
    
    index = 0
    for twt in tweets:
        found = False
        for t in last:
            if not twt or not t:
                continue
            if twt.id == t.id:
                found = True
                break
        if not found:
            index += 1
    
    return index
    
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

# -*- coding: utf-8 -*-

# Funciones utilitarias comúnes a todas las vistas
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2009

import re
import time
import datetime
import xml.sax.saxutils as saxutils

AVATAR_SIZE = 48

HASHTAG_PATTERN = re.compile('\#[\wáéíóúÁÉÍÓÚñÑçÇ]+')
MENTION_PATTERN = re.compile('\@(\w+)[\W\S]')
CLIENT_PATTERN = re.compile('<a href="(.*?)">(.*?)</a>')
URL_PATTERN = re.compile('((http|ftp|https)://[-A-Za-z0-9+&@#/%?=~_().]*[-A-Za-z0-9+&@#/%?=~_()])')

def detect_client(tweet):
    if not tweet.has_key('source'): return None
    text = saxutils.unescape(tweet['source'])
    text = text.replace('&quot;', '"')
    if text == 'web': return text
    rtn = CLIENT_PATTERN.search(text)
    if rtn: return rtn.groups()[1]
    return None
    
def detect_hashtags(text):
    return HASHTAG_PATTERN.findall(text)
    
def detect_mentions(text):
    return MENTION_PATTERN.findall(text)
    
def detect_urls(text):
    urls = []
    temp = URL_PATTERN.findall(text)
    for u in temp:
        urls.append(u[0])
    return urls
    
def get_rates(val):
    tsec = val['reset_time_in_seconds'] - time.timezone
    t = time.strftime('%I:%M %P', time.gmtime(tsec))
    hits = val['remaining_hits']
    limit = val['hourly_limit']
    return u"%s de %s llamadas a la API. Reset: %s" % (hits, limit, t)

def get_timestamp(tweet):
    # Tue Mar 13 00:12:41 +0000 2007 -> Tweets normales
    # Wed, 08 Apr 2009 19:22:10 +0000 -> Busquedas
    month_names = [None, 'Jan', 'Feb','Mar','Apr','May','Jun','Jul',
        'Aug','Sep','Oct','Nov','Dec']
    
    date_info = tweet['created_at'].split()
    
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
    if (time.daylight): i_hate_timezones = time.altzone
    
    dt = datetime.datetime(*d.timetuple()[:-3]) - datetime.timedelta(seconds=i_hate_timezones)
    t = dt.timetuple()
    
    return time.strftime('%b %d, %I:%M %p', t)

def count_new_tweets(tweets, last):
    if not last: return 0
    if (tweets is None) or (len(tweets) <= 0): return 0
    
    index = 0
    for twt in tweets:
        found = False
        for t in last:
            if twt['id'] == t['id']: found = True
        if not found: index += 1
    
    return index
    
def has_tweet(src, tweet):
    for t in src:
        if tweet['id'] == t['id']: return True
    return False
    
def escape_text(text):
    return saxutils.escape(text)
    
def unescape_text(text):
    return saxutils.unescape(text)

# -*- coding: utf-8 -*-

# Funciones utilitarias comúnes a todas las vistas
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2009

import re
import time
import datetime

HASHTAG_PATTERN = re.compile('\#(.*?)[\W]')
MENTION_PATTERN = re.compile('\@(.*?)[\W]')
CLIENT_PATTERN = re.compile('<a href="(.*?)">(.*?)</a>')

def detect_client(tweet):
    if not tweet.has_key('source'): return None
    text = tweet['source']
    if text == 'web': return text
    rtn = CLIENT_PATTERN.search(text)
    if rtn: return rtn.groups()[1]
    return None
    
def detect_hashtags(text):
    return HASHTAG_PATTERN.findall(text)
    
def detect_mentions(text):
    return MENTION_PATTERN.findall(text)
    
def get_rates(val):
    tsec = val['reset_time_in_seconds'] - time.timezone
    t = time.strftime('%I:%M %P', time.gmtime(tsec))
    hits = val['remaining_hits']
    limit = val['hourly_limit']
    return "%s of %s API calls. Next reset: %s" % (hits, limit, t)

# a=time.strptime('Sat Nov 07 14:55:06 +0000 2009', '%a %b %d %H:%M:%S +0000 %Y')
# time.mktime(a) -> Tiempo en segundos
# time.timezone -> Diferencia Horaria
# 
# time.strftime('%b %d, %I:%M %P', )
# time.strftime('%b %d, %H:%M', a)

def get_timestamp(tweet):
    # Tue Mar 13 00:12:41 +0000 2007
    date_info = tweet['created_at'].split()
    month_names = [None, 'Jan', 'Feb','Mar','Apr','May','Jun','Jul',
        'Aug','Sep','Oct','Nov','Dec']
    month = month_names.index(date_info[1])
    day = int(date_info[2])
    year = int(date_info[5])
    
    time_info = date_info[3].split(':')
    hour = int(time_info[0])
    minute = int(time_info[1])
    second = int(time_info[2])
    
    d = datetime.datetime(year, month, day, hour, minute, second)
    z = time.mktime(d.timetuple()) - time.timezone
    tm = time.strftime('%b %d, %I:%M %P', time.gmtime(z))
    #print tweet['created_at']
    #print z
    #print time.gmtime(z)
    #print tm
    return tm

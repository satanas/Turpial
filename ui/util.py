# -*- coding: utf-8 -*-

# Funciones utilitarias comúnes a todas las vistas
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2009

import re
import time

HASHTAG_PATTERN = re.compile('\#(.*?)[\W]')
MENTION_PATTERN = re.compile('\@(.*?)[\W]')
CLIENT_PATTERN = re.compile('<a href="(.*?)">(.*?)</a>')

def detect_client(text):
    if text == 'web': return text
    rtn = CLIENT_PATTERN.search(text)
    if rtn: return rtn.groups()[1]
    return 'unknown'
    
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

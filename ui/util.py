# -*- coding: utf-8 -*-

# Funciones utilitarias comúnes a todas las vistas
#
# Author: Wil Alvarez (aka Satanas)
# Nov 13, 2009

import re

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

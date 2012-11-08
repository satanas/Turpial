# -*- coding: utf-8 -*-

# Common functions or constants for GTK3 in Turpial

class StatusProgress:
    FAVING = 'adding_to_fav'
    UNFAVING = 'removing_from_fav'
    RETWEETING = 'retweeting'
    UNRETWEETING = 'unretweeting'
    DELETING = 'deleting'


def escape_text_for_markup(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

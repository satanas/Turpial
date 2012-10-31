# -*- coding: utf-8 -*-

# Common functions for GTK3 in Turpial

def escape_text_for_markup(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

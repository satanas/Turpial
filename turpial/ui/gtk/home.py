# -*- coding: utf-8 -*-

# Widget que representa las tres columnas del Home en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 03, 2010

from turpial.ui.gtk.tweetslist import TweetList
from turpial.ui.gtk.wrapper import Wrapper, WrapperAlign

try:
    import webkit
    from turpial.ui.gtk.tweetslistwk import TweetListWebkit
except:
    pass
    
class Home(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        if mainwin.extend:
            self.timeline = TweetListWebkit(mainwin, 'Timeline')
            self.replies = TweetListWebkit(mainwin, _('Mentions'))
        else:
            self.timeline = TweetList(mainwin, _('Timeline'))
            self.replies = TweetList(mainwin, _('Mentions'))
        self.direct = TweetList(mainwin, _('Directs'), 'direct')
        
        self._append_widget(self.timeline, WrapperAlign.left)
        self._append_widget(self.replies, WrapperAlign.middle)
        self._append_widget(self.direct, WrapperAlign.right)
        
        self.change_mode(mode)

# -*- coding: utf-8 -*-

# Widget que representa las tres columnas del Home en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Jun 03, 2010

from turpial.ui.gtk.columns import StandardColumn
from turpial.ui.gtk.wrapper import Wrapper, WrapperAlign

try:
    import webkit
    from turpial.ui.gtk.tweetslistwk import TweetListWebkit
except:
    pass
    
class Home(Wrapper):
    def __init__(self, mainwin, mode='single', viewed=None):
        Wrapper.__init__(self)
        
        if mainwin.extend:
            self.timeline = TweetListWebkit(mainwin, 'Timeline')
            self.replies = TweetListWebkit(mainwin, _('Mentions'))
        else:
            self.timeline = StandardColumn(mainwin, _('Timeline'), pos=0, 
                viewed=viewed)
            self.replies = StandardColumn(mainwin, _('Mentions'), pos=1, 
                viewed=viewed)
        self.direct = StandardColumn(mainwin, _('Directs'), pos=2, 
            viewed=viewed)
        
        self._append_widget(self.timeline, WrapperAlign.left)
        self._append_widget(self.replies, WrapperAlign.middle)
        self._append_widget(self.direct, WrapperAlign.right)
        
        self.change_mode(mode)
        
    def set_viewed_columns(self, lists, viewed):
        self.timeline.fill_combo(lists, viewed)
        self.replies.fill_combo(lists, viewed)
        self.direct.fill_combo(lists, viewed)
        
    def set_combo_item(self, index, reset):
        if index == 0:
            self.timeline.set_combo_item(reset)
        elif index == 1:
            self.replies.set_combo_item(reset)
        elif index == 2:
            self.direct.set_combo_item(reset)

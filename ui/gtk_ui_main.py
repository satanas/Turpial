# -*- coding: utf-8 -*-

# Vista para Turpial en PyGTK
#
# Author: Wil Alvarez (aka Satanas)
# Nov 08, 2009

import gtk
import util
import pango
import logging
import gobject

from base_ui import *
from gtk_ui import *

gtk.gdk.threads_init()

log = logging.getLogger('Gtk')

class SearchTweets(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.mainwin = mainwin
        self.input_topics = gtk.Entry()
        try:
            self.input_topics.set_property("primary-icon-stock", gtk.STOCK_FIND)
            self.input_topics.set_property("secondary-icon-stock", gtk.STOCK_CLEAR)
            self.input_topics.connect("icon-press", self.__on_icon_press)
        except: 
            pass
        
        inputbox = gtk.HBox(False)
        inputbox.pack_start(self.input_topics, True, True)
        
        self.topics = TweetList(mainwin, label)
        self.caption = label
        
        self.pack_start(inputbox, False, False)
        self.pack_start(self.topics, True, True)
        self.show_all()
        
        self.input_topics.connect('activate', self.__search_topic)
        
    def __on_icon_press(self, widget, pos, e):
        if pos == 0: 
            self.__search_topic(widget)
        elif pos == 1:
            widget.set_text('')
            
    def __search_topic(self, widget):
        topic = widget.get_text()
        self.mainwin.request_search_topic(topic)
        widget.set_text('')
        
    def update_tweets(self, arr_tweets):
        self.topics.update_tweets(arr_tweets)
        
    def update_user_pic(self, user, pic):
        self.topics.update_user_pic(user, pic)
        
    def update_wrap(self, width):
        self.topics.update_wrap(width)

class SearchPeople(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.mainwin = mainwin
        self.input_topics = gtk.Entry()
        try:
            self.input_topics.set_property("primary-icon-stock", gtk.STOCK_FIND)
            self.input_topics.set_property("secondary-icon-stock", gtk.STOCK_CLEAR)
            self.input_topics.connect("icon-press", self.__on_icon_press)
        except: 
            pass
        
        inputbox = gtk.HBox(False)
        inputbox.pack_start(self.input_topics, True, True)
        
        self.people = PeopleList(mainwin, label)
        self.caption = label
        
        self.pack_start(inputbox, False, False)
        self.pack_start(self.people, True, True)
        self.show_all()
        
        self.input_topics.connect('activate', self.__search_topic)
        
    def __on_icon_press(self, widget, pos, e):
        if pos == 0: 
            self.__search_topic(widget)
        elif pos == 1:
            widget.set_text('')
            
    def __search_topic(self, widget):
        query = widget.get_text()
        self.mainwin.request_search_people(query)
        widget.set_text('')
        
    def update_profiles(self, arr_profiles):
        self.people.update_profiles(arr_profiles)
        
    def update_user_pic(self, user, pic):
        self.people.update_user_pic(user, pic)
        
    def update_wrap(self, width):
        self.people.update_wrap(width)
        
class Trending(gtk.VBox):
    def __init__(self, mainwin, label=''):
        gtk.VBox.__init__(self, False)
        
        self.mainwin = mainwin
        self.caption = label
        update = gtk.Button(stock=gtk.STOCK_REFRESH)
        self.current = TrendingBox(mainwin, 'What\'s happening right now', 'trend-current.png')
        self.day = TrendingBox(mainwin, 'What happened today', 'trend-daily.png')
        self.week = TrendingBox(mainwin, 'What happened this week', 'trend-weekly.png')
        
        self.pack_start(self.current, False, False, 3)
        self.pack_start(self.day, False, False, 3)
        self.pack_start(self.week, False, False, 3)
        self.pack_start(update, False, False, 5)
        
        self.show_all()
        
        update.connect('clicked', self.__request_trends)
        
    def __request_trends(self, widget):
        self.mainwin.request_trends()
        
    def update_trends(self, current, day, week):
        self.current.update_topic(current)
        self.day.update_topic(day)
        self.week.update_topic(week)
        
    def update_wrap(self, w):
        pass
        
class TrendingBox(gtk.VBox):
    def __init__(self, mainwin, label='', icon=None):
        gtk.VBox.__init__(self, False)
        
        self.mainwin = mainwin
        self.trends = []
        for i in range(9):
            btn = gtk.Button('%i' % i)
            btn.connect('clicked', self.__search_topic)
            self.trends.append(btn)
            
        title = gtk.Label()
        title.set_alignment(0, 0.5)
        title.set_markup('<b>%s</b>' % label)
        
        titlebox = gtk.HBox(False)
        if icon:
            icon = util.load_image(icon)
            titlebox.pack_start(icon, False, False, 5)
        titlebox.pack_start(title, False, False)
        
        line1 = gtk.HBox(True)
        for i in range(3):
            line1.pack_start(self.trends[i])
        
        line2 = gtk.HBox(True)
        for i in range(3, 6):
            line2.pack_start(self.trends[i])
            
        line3 = gtk.HBox(True)
        for i in range(6, 9):
            line3.pack_start(self.trends[i])
            
        self.pack_start(titlebox, False, False, 2)
        self.pack_start(line1, False, False, 1)
        self.pack_start(line2, False, False, 1)
        self.pack_start(line3, False, False, 1)
        self.show_all()
        
    def __search_topic(self, widget):
        topic = widget.get_label()
        self.mainwin.request_search_topic(topic)
        
    def update_topic(self, arr_topics):
        for result in arr_topics['trends']:
            arr = arr_topics['trends'][result]
            for i in range(9):
                topic = arr[i]['name']
                self.trends[i].set_label(topic)
        
# ------------------------------------------------------------
# Objetos del Dock (Main Objects)
# ------------------------------------------------------------
class Home(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.timeline = TweetList(mainwin, 'Home')
        self.replies = TweetList(mainwin, 'Replies')
        self.direct = TweetList(mainwin, 'Direct')
        
        self._append_widget(self.timeline, WrapperAlign.left)
        self._append_widget(self.replies, WrapperAlign.middle)
        self._append_widget(self.direct, WrapperAlign.right)
        
        self.change_mode(mode)
        
class Favorites(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.favorites = TweetList(mainwin, 'Favorites')
        self.lfy = TweetList(mainwin, 'List following you')
        self.lyf = TweetList(mainwin, 'List you follow')
        
        self._append_widget(self.favorites, WrapperAlign.left)
        self._append_widget(self.lfy, WrapperAlign.middle)
        self._append_widget(self.lyf, WrapperAlign.right)
        
        self.change_mode(mode)
'''
class Retweets(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.by_me = TweetList(mainwin, 'Retweets by me')
        self.to_me = TweetList(mainwin, 'Retweets to me')
        self.of_me = TweetList(mainwin, 'Retweets of me')
        
        self._append_widget(self.by_me, WrapperAlign.left)
        self._append_widget(self.to_me, WrapperAlign.middle)
        self._append_widget(self.of_me, WrapperAlign.right)
        
        self.change_mode(mode)
'''
class Profile(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.user_form = UserForm(mainwin, 'Profile')
        self.following = PeopleList(mainwin, 'Following')
        self.followers = PeopleIcons(mainwin, 'Followers')
        
        self._append_widget(self.user_form, WrapperAlign.left)
        self._append_widget(self.following, WrapperAlign.middle)
        self._append_widget(self.followers, WrapperAlign.right)
        
        self.change_mode(mode)
        
    def set_user_profile(self, user_profile):
        self.user_form.update(user_profile)
        
    def set_following(self, arr_following):
        self.following.update_profiles(arr_following)
        
    def set_followers(self, arr_followers):
        self.followers.update_profiles(arr_followers)
        
class Search(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.trending = Trending(mainwin, 'Trending')
        self.topics = SearchTweets(mainwin, 'Topics')
        self.people = SearchPeople(mainwin, 'People')
        
        self._append_widget(self.trending, WrapperAlign.left)
        self._append_widget(self.topics, WrapperAlign.middle)
        self._append_widget(self.people, WrapperAlign.right)
        
        self.change_mode(mode)
        
class Main(BaseGui, gtk.Window):
    def __init__(self, controller):
        BaseGui.__init__(self, controller)
        gtk.Window.__init__(self)
        
        self.set_title('Turpial')
        self.set_size_request(280, 350)
        self.set_default_size(320, 480)
        self.set_icon(util.load_image('turpial_icon.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect('destroy', self.quit)
        self.connect('size-request', self.size_request)
        
        self.mode = 0
        self.vbox = None
        self.workspace = 'wide'
        self.contentbox = gtk.VBox(False)
        
        self.home = Home(self, self.workspace)
        self.favs = Favorites(self)
        self.profile = Profile(self)
        self.search = Search(self)
        self.contenido = self.home
        self.updatebox = UpdateBox(self)
        
        self.dock = Dock(self, self.workspace)
        
    def quit(self, widget):
        self.hide()
        gtk.main_quit()
        self.request_signout()
        exit(0)
        
    def main_loop(self):
        gtk.main()
        
    def show_login(self):
        self.mode = 1
        if self.vbox is not None: self.remove(self.vbox)
        
        avatar = util.load_image('logo.png')
        self.message = LoginLabel(self)
        
        lbl_user = gtk.Label()
        lbl_user.set_justify(gtk.JUSTIFY_LEFT)
        lbl_user.set_use_markup(True)
        lbl_user.set_markup('<span size="small">Username</span>')
        
        lbl_pass = gtk.Label()
        lbl_pass.set_justify(gtk.JUSTIFY_LEFT)
        lbl_pass.set_use_markup(True)
        lbl_pass.set_markup('<span size="small">Password</span>')
        
        self.username = gtk.Entry()
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        
        self.btn_signup = gtk.Button('Conectar')
        
        table = gtk.Table(8,1,False)
        table.attach(avatar,0,1,0,1,gtk.FILL,gtk.FILL, 20, 10)
        table.attach(self.message,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 3)
        table.attach(lbl_user,0,1,2,3,gtk.EXPAND,gtk.FILL,0,0)
        table.attach(self.username,0,1,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 0)
        table.attach(lbl_pass,0,1,4,5,gtk.EXPAND,gtk.FILL, 0, 5)
        table.attach(self.password,0,1,5,6,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 0)
        table.attach(self.btn_signup,0,1,7,8,gtk.EXPAND,gtk.FILL,0, 30)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(table, False, False, 2)
        
        self.add(self.vbox)
        self.show_all()
        
        self.btn_signup.connect('clicked', self.signin, self.username, self.password)
        self.password.connect('activate', self.signin, self.username, self.password)
        
    def signin(self, widget, username, password):
        self.btn_signup.set_sensitive(False)
        self.username.set_sensitive(False)
        self.password.set_sensitive(False)
        self.request_signin(username.get_text(), password.get_text())
        
    def cancel_login(self, error):
        #e = '<span background="#C00" foreground="#FFF" size="small">%s</span>' % error
        self.message.set_error(error)
        self.btn_signup.set_sensitive(True)
        self.username.set_sensitive(True)
        self.password.set_sensitive(True)
        
    def show_main(self):
        log.debug('Cargando ventana principal')
        self.mode = 2
        
        self.contentbox.add(self.contenido)
        
        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0, 'Turpial')
        if (self.vbox is not None): self.remove(self.vbox)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(self.contentbox, True, True, 0)
        self.vbox.pack_start(self.dock, False, False, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        
        self.add(self.vbox)
        self.switch_mode()
        self.show_all()
        
        gobject.timeout_add(3*60*1000, self.download_timeline)
        gobject.timeout_add(5*60*1000, self.download_rates)
        gobject.timeout_add(10*60*1000, self.download_replies)
        gobject.timeout_add(15*60*1000, self.download_directs)
        
        
    def show_home(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.home
        self.contentbox.add(self.contenido)
        
    def show_favs(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.favs
        self.contentbox.add(self.contenido)
        
    def show_profile(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.profile
        self.contentbox.add(self.contenido)
    
    def show_search(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.search
        self.contentbox.add(self.contenido)
        
    def show_update_box(self, text='', id='', user=''):
        if self.updatebox.get_property('visible'): 
            self.updatebox.present()
            return
        self.updatebox.show(text, id, user)
        
    def update_timeline(self, tweets):
        if tweets is None: return
        log.debug(u'Actualizando el timeline')
        self.home.timeline.update_tweets(tweets)
        
    def update_replies(self, tweets):
        if tweets is None: return
        log.debug(u'Actualizando las replies')
        self.home.replies.update_tweets(tweets)
        
    def update_favs(self, tweets):
        if tweets is None: return
        log.debug(u'Actualizando favoritos')
        self.favs.favorites.update_tweets(tweets)
        
    def update_directs(self, sent, recv):
        if recv is None: return
        log.debug(u'Actualizando mensajes directos')
        self.home.direct.update_tweets(sent)
        
    def update_user_profile(self, profile):
        if profile is None: return
        log.debug(u'Actualizando perfil del usuario')
        self.profile.set_user_profile(profile)
        
    def update_following(self, people):
        if people is None: return
        log.debug(u'Actualizando following')
        self.profile.set_following(people)
        
    def update_followers(self, people):
        if people is None: return
        log.debug(u'Actualizando followers')
        self.profile.set_followers(people)
        
    def update_rate_limits(self, val):
        if val is None: return
        self.statusbar.push(0, util.get_rates(val))
        
    def update_search_topics(self, val):
        if val is None: return
        self.search.topics.update_tweets(val['results'])
        self.show_search(self)
        if self.workspace != 'wide':
            self.contenido.wrapper.set_current_page(1)
            
    def update_search_people(self, val):
        if val is None: return
        self.search.people.update_profiles(val)
        #self.show_search(self)
        #if self.workspace != 'wide':
        #    self.contenido.wrapper.set_current_page(1)
        
    def update_trends(self, current, day, week):
        self.search.trending.update_trends(current, day, week)
        
    def get_user_avatar(self, user, pic_url):
        pix = self.request_user_avatar(user, pic_url)
        if pix:
            return util.load_avatar(pix)
        else:
            return util.load_image('unknown.png', pixbuf=True)
        
    def update_user_avatar(self, user, pic):
        self.home.timeline.update_user_pic(user, pic)
        self.home.replies.update_user_pic(user, pic)
        self.home.direct.update_user_pic(user, pic)
        self.favs.favorites.update_user_pic(user, pic)
        self.profile.following.update_user_pic(user, pic)
        self.profile.followers.update_user_pic(user, pic)
        self.profile.user_form.update_user_pic(user, pic)
        self.search.topics.update_user_pic(user, pic)
        self.search.people.update_user_pic(user, pic)
        
    def switch_mode(self, widget=None):
        cur_x, cur_y = self.get_position()
        cur_w, cur_h = self.get_size()
        
        if self.workspace == 'single':
            self.workspace = 'wide'
            self.set_size_request(960, 480)
            self.resize(960, 480)
            x = (960 - cur_w)/2
            self.move(cur_x - x, cur_y)
        else:
            self.workspace = 'single'
            self.set_size_request(320, 480)
            self.resize(320, 480)
            x = (cur_w - 320)/2
            self.move(cur_x + x, cur_y)
        
        self.dock.change_mode(self.workspace)
        self.home.change_mode(self.workspace)
        self.favs.change_mode(self.workspace)
        self.search.change_mode(self.workspace)
        self.profile.change_mode(self.workspace)
        self.show_all()
        
    def size_request(self, widget, event, data=None):
        """Callback when the window changes its sizes. We use it to set the
        proper word-wrapping for the message column."""
        if self.mode < 2: return
        
        w, h = self.get_size()
        self.contenido.update_wrap(w, self.workspace)
        return
        

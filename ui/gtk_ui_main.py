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
import webbrowser

from gtk_ui import *
from base_ui import *
from notification import *

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

'''
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
'''
# ------------------------------------------------------------
# Objetos del Dock (Main Objects)
# ------------------------------------------------------------
class Home(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.timeline = TweetList(mainwin, 'Home')
        self.replies = TweetList(mainwin, 'Replies')
        self.direct = TweetList(mainwin, 'Direct', False)
        
        self._append_widget(self.timeline, WrapperAlign.left)
        self._append_widget(self.replies, WrapperAlign.middle)
        self._append_widget(self.direct, WrapperAlign.right)
        
        self.change_mode(mode)
        
class Profile(Wrapper):
    def __init__(self, mainwin, mode='single'):
        Wrapper.__init__(self)
        
        self.favorites = TweetList(mainwin, 'Favorites')
        self.user_form = UserForm(mainwin, 'Profile')
        self.topics = SearchTweets(mainwin, 'Topics')
        
        self._append_widget(self.favorites, WrapperAlign.left)
        self._append_widget(self.user_form, WrapperAlign.middle)
        self._append_widget(self.topics, WrapperAlign.right)
        
        self.change_mode(mode)
        
    def set_user_profile(self, user_profile):
        self.user_form.update(user_profile)
        
        
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
        self.workspace = 'single'
        self.contentbox = gtk.VBox(False)
        
        self.showed = True
        self.home_timer = None
        self.replies_timer = None
        self.directs_timer = None
        self.home_interval = 3
        self.replies_interval = 10
        self.directs_interval = 15
        
        self.notify = Notification()
        
        self.home = Home(self, self.workspace)
        self.profile = Profile(self)
        self.contenido = self.home
        self.updatebox = UpdateBox(self)
        
        self.dock = Dock(self, self.workspace)
        self.__create_trayicon()
        
    def filter_cb(self, event, data=None):
        print 'me again7', event.type, event, data
        return gtk.gdk.FILTER_CONTINUE
        
    def __create_trayicon(self):
        if gtk.check_version(2, 10, 0) is not None:
            self.log.debug("Disabled Tray Icon. It needs PyGTK >= 2.10.0")
            return
        self.tray = gtk.StatusIcon()
        self.tray.set_from_pixbuf(util.load_image('turpial_icon.png', True))
        self.tray.set_tooltip('%s %s' % ('Turpial', '0.8'))
        self.tray.connect("activate", self.__on_trayicon_click)
        self.tray.connect("popup-menu", self.__show_tray_menu)
        
        
    def __on_trayicon_click(self, widget):
        if(self.showed is True):
            self.showed = False
            self.hide()
        else:
            self.showed = True
            self.show()
            #self.present()
            
    def __show_tray_menu(self, widget, button, activate_time):
        menu = gtk.Menu()
        tweet = gtk.MenuItem('Tweet')
        exit = gtk.MenuItem('Exit')
        if self.mode == 2:
            menu.append(tweet)
        menu.append(exit)
        
        exit.connect('activate', self.quit)
        tweet.connect('activate', self.show_update_box)
            
        menu.show_all()
        menu.popup(None, None, None, button, activate_time)
        
    def quit(self, widget):
        self.request_signout()
        gtk.main_quit()
        self.destroy()
        self.tray = None
        
    def main_loop(self):
        gtk.main()
        
    def show_login(self):
        x = gtk.gdk.get_default_root_window()
        x.set_events(gtk.gdk.KEY_PRESS_MASK |
             gtk.gdk.POINTER_MOTION_MASK |
             gtk.gdk.BUTTON_PRESS_MASK |
             gtk.gdk.SCROLL_MASK)

        x.add_filter(self.filter_cb, 'passthisforward')
        
        self.mode = 1
        if self.vbox is not None: self.remove(self.vbox)
        
        avatar = util.load_image('logo2.png')
        self.message = LoginLabel(self)
        
        lbl_user = gtk.Label()
        #lbl_user.set_justify(gtk.JUSTIFY_LEFT)
        lbl_user.set_use_markup(True)
        lbl_user.set_markup('<span size="small">Username and Password</span>')
        lbl_user.set_alignment(0, 0.5)
        
        lbl_pass = gtk.Label()
        lbl_pass.set_justify(gtk.JUSTIFY_LEFT)
        lbl_pass.set_use_markup(True)
        lbl_pass.set_markup('<span size="small">Password</span>')
        
        self.username = gtk.Entry()
        self.password = gtk.Entry()
        self.password.set_visibility(False)
        
        self.btn_signup = gtk.Button('Conectar')
        self.btn_oauth = gtk.Button('Autenticar usando OAuth')
        
        self.waiting = CairoWaiting(self)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        hbox = gtk.HBox(False)
        hbox.pack_start(lbl_user, False, False, 2)
        hbox.pack_start(align, True, True, 2)
        
        table = gtk.Table(9,1,False)
        table.attach(avatar,0,1,0,1,gtk.FILL,gtk.FILL, 10, 50)
        table.attach(self.message,0,1,1,2,gtk.EXPAND|gtk.FILL,gtk.FILL, 20, 3)
        table.attach(hbox,0,1,2,3,gtk.EXPAND|gtk.FILL,gtk.FILL,50,0)
        table.attach(self.username,0,1,3,4,gtk.EXPAND|gtk.FILL,gtk.FILL, 50, 0)
        #table.attach(lbl_pass,0,1,4,5,gtk.EXPAND,gtk.FILL, 0, 5)
        table.attach(self.password,0,1,5,6,gtk.EXPAND|gtk.FILL,gtk.FILL, 50, 0)
        table.attach(self.btn_signup,0,1,7,8,gtk.EXPAND,gtk.FILL,0, 10)
        table.attach(self.btn_oauth,0,1,8,9,gtk.EXPAND,gtk.FILL,0, 10)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(table, False, False, 2)
        
        self.add(self.vbox)
        self.show_all()
        
        self.btn_signup.connect('clicked', self.signin, self.username, self.password)
        self.btn_oauth.connect('clicked', self.oauth, self.username, self.password)
        self.password.connect('activate', self.signin, self.username, self.password)
        
    def signin(self, widget, username, password):
        self.message.deactivate()
        self.waiting.start()
        self.btn_signup.set_sensitive(False)
        self.btn_oauth.set_sensitive(False)
        self.username.set_sensitive(False)
        self.password.set_sensitive(False)
        self.request_signin(username.get_text(), password.get_text())
        
    def oauth(self, widget, username, password):
        self.message.deactivate()
        self.waiting.start()
        self.btn_signup.set_sensitive(False)
        self.btn_oauth.set_sensitive(False)
        self.username.set_sensitive(False)
        self.password.set_sensitive(False)
        self.request_oauth(username.get_text(), password.get_text())
        
    def cancel_login(self, error):
        self.message.set_error(error)
        self.waiting.stop(error=True)
        self.btn_signup.set_sensitive(True)
        self.btn_oauth.set_sensitive(True)
        self.username.set_sensitive(True)
        self.password.set_sensitive(True)
        
    def show_main(self, config, p):
        log.debug('Cargando ventana principal')
        self.mode = 2
        gtk.gdk.threads_enter()
        self.contentbox.add(self.contenido)
        
        self.statusbar = gtk.Statusbar()
        self.statusbar.push(0, 'Turpial')
        if (self.vbox is not None): self.remove(self.vbox)
        
        self.vbox = gtk.VBox(False, 5)
        self.vbox.pack_start(self.contentbox, True, True, 0)
        self.vbox.pack_start(self.dock, False, False, 0)
        self.vbox.pack_start(self.statusbar, False, False, 0)
        
        self.add(self.vbox)
        self.show_all()
        gtk.gdk.threads_leave()
        self.update_config(config)
        
        self.notify.popup('@%s' % p['screen_name'], 
            'Tweets: %i\nFollowing: %i\nFollowers: %i' % (p['statuses_count'], 
            p['friends_count'], p['followers_count'])
        )
        
        gobject.timeout_add(6*60*1000, self.download_rates)
        
    def show_home(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.home
        self.contentbox.add(self.contenido)
        
    def show_profile(self, widget):
        self.contentbox.remove(self.contenido)
        self.contenido = self.profile
        self.contentbox.add(self.contenido)
        
    def show_update_box(self, text='', id='', user=''):
        if self.updatebox.get_property('visible'): 
            self.updatebox.present()
            return
        self.updatebox.show(text, id, user)
        
    def show_prefs(self, widget):
        prefs = Preferences(self)
        
    def show_oauth_pin_request(self, url):
        webbrowser.open(url)
        gtk.gdk.threads_enter()
        p = InputPin(self)
        response = p.run()
        if response == gtk.RESPONSE_ACCEPT:
            verifier = p.pin.get_text()
        else:
            self.cancel_login('Login cancelado por el usuario')
            return
            
        if verifier == '': 
            self.cancel_login('Debe escribir el PIN válido')
            return
        print 'verifier', verifier
        p.destroy()
        gtk.gdk.threads_leave()
        self.request_auth_token(verifier)
        
    def start_updating_timeline(self):
        self.home.timeline.waiting.start()
        
    def start_updating_replies(self):
        self.home.replies.waiting.start()
        
    def start_updating_directs(self):
        self.home.direct.waiting.start()
        
    def update_timeline(self, tweets):
        log.debug(u'Actualizando el timeline')
        gtk.gdk.threads_enter()
        count = self.home.timeline.update_tweets(tweets)
        self.notify.new_tweets(count, self.updating['home'])
        gtk.gdk.threads_leave()
        self.updating['home'] = False
        
    def update_replies(self, tweets):
        log.debug(u'Actualizando las replies')
        gtk.gdk.threads_enter()
        count = self.home.replies.update_tweets(tweets)
        self.notify.new_replies(count, self.updating['replies'])
        gtk.gdk.threads_leave()
        self.updating['replies'] = False
        
    def update_directs(self, recv):
        log.debug(u'Actualizando mensajes directos')
        gtk.gdk.threads_enter()
        count = self.home.direct.update_tweets(recv)
        self.notify.new_directs(count, self.updating['directs'])
        gtk.gdk.threads_leave()
        self.updating['directs'] = False
        
    def update_favorites(self, tweets):
        log.debug(u'Actualizando favoritos')
        self.profile.favorites.update_tweets(tweets)
        
    def update_user_profile(self, profile):
        log.debug(u'Actualizando perfil del usuario')
        self.profile.set_user_profile(profile)
        
    def update_following(self, people):
        log.debug(u'Actualizando following')
        self.profile.set_following(people)
        
    def update_followers(self, people):
        log.debug(u'Actualizando followers')
        self.profile.set_followers(people)
        
    def update_rate_limits(self, val):
        if val is None: return
        self.statusbar.push(0, util.get_rates(val))
        
    def update_search_topics(self, val):
        self.search.topics.update_tweets(val['results'])
        self.show_search(self)
        if self.workspace != 'wide':
            self.contenido.wrapper.set_current_page(1)
            
    def update_search_people(self, val):
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
        self.profile.favorites.update_user_pic(user, pic)
        self.profile.user_form.update_user_pic(user, pic)
        self.profile.topics.update_user_pic(user, pic)
        
    def tweet_changed(self, timeline, replies, favs):
        log.debug(u'Tweet modificado')
        gtk.gdk.threads_enter()
        log.debug(u'--Actualizando el timeline')
        self.home.timeline.update_tweets(timeline)
        log.debug(u'--Actualizando las replies')
        self.home.replies.update_tweets(replies)
        log.debug(u'--Actualizando favoritos')
        self.profile.favorites.update_tweets(favs)
        gtk.gdk.threads_leave()
        
    def tweet_fav(self, id, fav):
        if fav:
            self.home.timeline.do_mark(id)
            self.home.replies.do_mark(id)
            self.profile.favorites.do_mark( id)
            self.request_fav(id)
        else:
            self.home.timeline.do_unmark(id)
            self.home.replies.do_unmark(id)
            self.profile.favorites.do_unmark(id)
            self.request_unfav(id)
        
    def switch_mode(self, widget=None):
        if self.workspace == 'single':
            self.workspace = 'wide'
        else:
            self.workspace = 'single'
        self.set_mode()
        
    def set_mode(self):
        cur_x, cur_y = self.get_position()
        cur_w, cur_h = self.get_size()
        
        if self.workspace == 'wide':
            self.set_size_request(960, 480)
            self.resize(960, 480)
            x = (960 - cur_w)/2
            self.move(cur_x - x, cur_y)
        else:
            self.set_size_request(320, 480)
            self.resize(320, 480)
            x = (cur_w - 320)/2
            self.move(cur_x + x, cur_y)
        
        self.dock.change_mode(self.workspace)
        self.home.change_mode(self.workspace)
        self.profile.change_mode(self.workspace)
        self.show_all()
        
    def update_config(self, config):
        log.debug('Actualizando configuracion')
        #self.workspace = config.read('General', 'workspace')
        #home_interval = int(config.read('General', 'home-update-interval'))
        #replies_interval = int(config.read('General', 'replies-update-interval'))
        #directs_interval = int(config.read('General', 'directs-update-interval'))
        
        self.workspace = 'single'
        home_interval = 3
        replies_interval = 10
        directs_interval = 15
        
        gtk.gdk.threads_enter()
        self.set_mode()
        
        if self.home_timer: gobject.remove_source(self.home_timer)
        if self.replies_timer: gobject.remove_source(self.home_timer)
        if self.directs_timer: gobject.remove_source(self.home_timer)
        
        if (self.home_interval != home_interval) or not self.home_timer:
            self.home_interval = home_interval
            self.home_timer = gobject.timeout_add(self.home_interval*60*1000, self.download_timeline)
            
        if (self.replies_interval != replies_interval) or not self.replies_timer:
            self.replies_interval = replies_interval
            self.replies_timer = gobject.timeout_add(self.replies_interval*60*1000, self.download_replies)
            
        if (self.directs_interval != directs_interval) or not self.directs_timer:
            self.directs_interval = directs_interval
            self.directs_timer = gobject.timeout_add(self.directs_interval*60*1000, self.download_directs)
            
        gtk.gdk.threads_leave()
        
    def size_request(self, widget, event, data=None):
        """Callback when the window changes its sizes. We use it to set the
        proper word-wrapping for the message column."""
        if self.mode < 2: return
        
        w, h = self.get_size()
        self.contenido.update_wrap(w, self.workspace)
        return

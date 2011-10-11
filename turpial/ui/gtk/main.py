# -*- coding: utf-8 -*-

# GTK main view for Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Sep 03, 2011

import os
import gtk
import sys
import Queue
import logging
import threading

from turpial.ui.lang import i18n
from turpial.ui.base import Base
from turpial.ui.html import HtmlParser
from turpial.ui.gtk.about import About
from turpial.ui.gtk.htmlview import HtmlView
from libturpial.common import ColumnType

gtk.gdk.set_program_class("Turpial")
gtk.gdk.threads_init()

log = logging.getLogger('Gtk')

class Main(Base, gtk.Window):
    def __init__(self, core):
        Base.__init__(self, core)
        gtk.Window.__init__(self)
        
        self.htmlparser = HtmlParser(core.list_protocols())
        self.set_title('Turpial')
        self.set_size_request(280, 350)
        self.set_default_size(352, 482)
        self.set_icon(self.load_image('turpial.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        self.connect('key-press-event', self.__on_key_press)
        self.connect('focus-in-event', self.__on_focus)
        
        self.container = HtmlView(uri='file://' + os.path.dirname(__file__))
        self.container.connect('action-request', self.__action_request)
        self.container.connect('link-request', self.__link_request)
        self.add(self.container)
        
        self.mode = 0
        
        # Configuration
        self.showed = True
        self.minimize = 'on'
        self.version = '2.x'
        
        self.timer1 = None
        self.timer2 = None
        self.timer3 = None
        self.interval1 = -1
        self.interval2 = -1
        self.interval3 = -1
        
        '''
        self.win_state = 'windowed'
        self.workspace = 'single'
        self.link_color = '#ff6633'
        '''
        
        #self.sound = Sound()
        #self.notify = Notification(controller.no_notif)
        
        self.worker = Worker()
        self.worker.start()
        
        self.__create_trayicon()
        self.show_all()
        
        self.tweet_template = '''<table>
    <tr>
        <td valign="top" class="tweet"><img src="${avatar}" width="48" height="48"/></td>
        <td valign="top" class="tweet desc">
            <span>
                <span class="mention"><b>@${username}</b></span> 
                ${text}<br/>
                <div class="spacer"/>
                <span class="footer">${date} ${client} ${in_reply_to}<br/>
                    ${retweeted_by}
                    <span class="buttons">
                        <a href="cmd:+fav">+fav</a> &nbsp;
                        <a href="cmd:retweet">retweet</a> &nbsp;
                        <a href="cmd:rt">RT </a> &nbsp;
                        <a href="cmd:reply">responder</a></span>
                </span>
            </span></td>
    </tr>
</table>'''
    
    def __action_request(self, widget, url):
        action = url.split(':')[0]
        try:
            args = url.split(':')[1].split('-%&%-')
        except IndexError:
            args = []
        print url
        print action, args
        
        if action == 'about':
            self.show_about()
        elif action == 'preferences':
            self.container.execute("alert('hola');")
        elif action == 'save_account':
            rem = True if args[3] == 'true' else False
            self.core.register_account(args[0], args[2], args[1], rem)
            page = self.htmlparser.render_account_list(self.core.all_accounts())
            self.container.execute("close_account_dialog();")
            self.container.update_element("form", page)
        elif action == 'delete_account':
            self.core.unregister_account(args[0], True)
            page = self.htmlparser.render_account_list(self.core.all_accounts())
            self.container.update_element("form", page)
        elif action == 'login':
            acc_login = []
            for acc in self.core.all_accounts():
                if acc.id_ in args:
                    acc_login.append(acc)
                    acc.activate(True)
                    if not acc.is_remembered():
                        print "ask for password for %s" % acc.id_
                else:
                    acc.activate(False)
            for acc in acc_login:
                print "login with %s" % acc.id_
    
    def __link_request(self, widget, url):
        print 'requested link: %s' % url
        
    def __create_trayicon(self):
        if gtk.check_version(2, 10, 0) is not None:
            log.debug("Disabled Tray Icon. It needs PyGTK >= 2.10.0")
            return
        self.tray = gtk.StatusIcon()
        self.tray.set_from_pixbuf(self.load_image('turpial-tray.png', True))
        self.tray.set_tooltip('Turpial')
        self.tray.connect("activate", self.__on_trayicon_click)
        self.tray.connect("popup-menu", self.__show_tray_menu)
        
    def __on_trayicon_click(self, widget):
        if self.showed:
            self.showed = False
            self.hide()
        else:
            self.showed = True
            self.show()
            
    def __on_focus(self, widget, event):
        self.tray.set_from_pixbuf(self.load_image('turpial-tray.png', True))
    
    def __on_key_press(self, widget, event):
        keyname = gtk.gdk.keyval_name(event.keyval)
        if (event.state & gtk.gdk.CONTROL_MASK) and keyname.lower() == 'n':
            self.show_update_box()
            return True
        return False
        
    def __show_tray_menu(self, widget, button, activate_time):
        menu = gtk.Menu()
        tweet = gtk.MenuItem(i18n.get('tweet'))
        follow = gtk.MenuItem(i18n.get('follow'))
        exit_ = gtk.MenuItem(i18n.get('exit'))
        if self.mode == 2:
            menu.append(tweet)
            menu.append(follow)
            menu.append(gtk.SeparatorMenuItem())
        menu.append(exit_)
        
        exit_.connect('activate', self.main_quit)
        #tweet.connect('activate', self.__show_update_box_from_menu)
        #follow.connect('activate', self.__show_follow_box_from_menu)
        
        menu.show_all()
        menu.popup(None, None, None, button, activate_time)
        
    def __close(self, widget, event=None):
        if self.minimize == 'on':
            self.showed = False
            self.hide()
        else:
            self.main_quit()
        return True
        
    def main_quit(self, widget=None):
        self.log.debug('Exit')
        self.destroy()
        self.tray = None
        self.worker.quit()
        self.worker.join()
        if widget:
            gtk.main_quit()
        sys.exit(0)
        
    def main_loop(self):
        try:
            gtk.gdk.threads_enter()
            gtk.main()
            gtk.gdk.threads_leave()
        except Exception:
            sys.exit(0)
    
    def show_login(self):
        page = self.htmlparser.login(self.core.all_accounts())
        self.container.render(page)
        
    def show_about(self):
        about = About(self)
        
    def load_image(self, path, pixbuf=False):
        img_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            '..', '..', 'data', 'pixmaps', path))
        pix = gtk.gdk.pixbuf_new_from_file(img_path)
        if pixbuf: return pix
        avatar = gtk.Image()
        avatar.set_from_pixbuf(pix)
        del pix
        return avatar
        
    def update_column1(self, statuses):
        if not statuses:
            print "There are no statuses to show"
            return
        
        if statuses.code > 0:
            print statuses.errmsg
            return
        
        page = self.page
        for status in statuses:
            text = status.text.replace('\n', ' ')
            inreply = ''
            client = ''
            retweeted = ''
            if status.in_reply_to_user:
                inreply = ' in reply to %s' % status.in_reply_to_user
            if status.source:
                client = ' from %s' % status.source
            if status.reposted_by:
                users = ''
                for u in status.reposted_by:
                    users += u + ' '
                retweeted = 'Retweeted by %s' % status.reposted_by
            
            twt = self.tweet_template
            twt = twt.replace('${avatar}', status.avatar)
            twt = twt.replace('${username}', status.username)
            twt = twt.replace('${text}', text)
            twt = twt.replace('${date}', status.datetime)
            twt = twt.replace('${client}', client)
            twt = twt.replace('${in_reply_to}', inreply)
            twt = twt.replace('${retweeted_by}', retweeted)
            page += twt
        gobject.idle_add(self.view.load_string, page, "text/html", "iso-8859-15", 'file://')
        
class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(False)
        self.queue = Queue.Queue()
        self.exit_ = False 
    
    def register(self, funct, args, callback):
        self.queue.put((funct, args, callback))
        
    def quit(self):
        self.exit_ = True
        
    def run(self):
        while not self.exit_:
            try:
                req = self.queue.get(True, 0.3)
            except Queue.Empty:
                continue
            except:
                continue
            
            (funct, args, callback) = req
            
            rtn = funct(args)
            if callback:
                callback(rtn)


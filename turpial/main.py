# -*- coding: utf-8 -*-

# Vista para Turpial usando Webkit
#
# Author: Wil Alvarez (aka Satanas)
# Sep 03, 2011

import os
import gtk
import sys
import Queue
#import base64
import logging
import gobject
import threading

from sound import Sound
from webcontainer import WebContainer
#from libturpial.api.core import Core
from libturpial.common import ColumnType

gtk.gdk.set_program_class("Turpial")
gtk.gdk.threads_init()

log = logging.getLogger('Gtk')

class Main(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        
        self.set_title('Turpial')
        self.set_size_request(280, 350)
        self.set_default_size(352, 482)
        self.set_icon(self.load_image('turpial.png', True))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.connect('delete-event', self.__close)
        self.connect('key-press-event', self.__on_key_press)
        self.connect('focus-in-event', self.__on_focus)
        
        
        self.container = WebContainer()
        self.add(self.container)
        
        self.mode = 0
        
        # Valores de config. por defecto
        self.showed = True
        self.win_state = 'windowed'
        self.minimize = 'on'
        self.workspace = 'single'
        self.link_color = '#ff6633'
        self.home_interval = -1
        self.replies_interval = -1
        self.directs_interval = -1
        self.me = None
        self.version = None
        
        self.home_timer = None
        self.replies_timer = None
        self.directs_timer = None
        
        self.sound = Sound()
        #self.notify = Notification(controller.no_notif)
        
        #self.wcore = Worker()
        #self.wcore.start()
        ##self.app_cfg = ConfigApp()
        ##self.version = self.app_cfg.read('App', 'version')
        
        self.__create_trayicon()
        self.show_all()
        '''
        #gobject.idle_add(self.view.load_string, '<img src="data/pixmaps/ajax-loader.gif">', "text/html", "iso-8859-15", os.path.dirname(__file__))
        filepath = "file://" + os.getcwd() + "/data/pixmaps/ajax-loader.gif"
        print '<img src= "%s">' % filepath
        style = "file://" + os.getcwd() + "/data/themes/default/style.css"
        self.page = '<html><head><link href="' + style + '" rel="stylesheet" type="text/css"></head><body>'
        #page = self.page
        #page += '<div class="test"><img src="'+filepath+'"></div></body></html>'
        fd = open('data/themes/default/login-test2.html', 'r')
        page = fd.read()
        fd.close()
        page = page.replace('../..', "file://" + os.getcwd() + "/data")
        gobject.idle_add(self.view.load_string, page, "text/html", "iso-8859-15", 'file://')
        '''
        
        self.container.load_layout('login')
        self.container.render()
        
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
        
    def __popo(self, widget):
        self.wcore.login()
        self.wcore.get_public(self.update_column1)
        
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
        tweet = gtk.MenuItem(('Tweet'))
        follow = gtk.MenuItem(('Follow'))
        exit = gtk.MenuItem(('Exit'))
        if self.mode == 2:
            menu.append(tweet)
            menu.append(follow)
            menu.append(gtk.SeparatorMenuItem())
        menu.append(exit)
        
        exit.connect('activate', self.main_quit)
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
        #self.__save_config()
        self.destroy()
        self.tray = None
        #self.wcore.quit()
        if widget:
            gtk.main_quit()
        #self.request_signout()
        #self.wcore.join()
        sys.exit(0)
        
    def main_loop(self):
        try:
            gtk.gdk.threads_enter()
            gtk.main()
            gtk.gdk.threads_leave()
        except Exception:
            sys.exit(0)
    
    def load_image(self, path, pixbuf=False):
        img_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
            'data', 'pixmaps', path))
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
        self.exit = False
        self.core = Core()
        self.account = self.core.register_account('satanas82', 'ferrari615448935', 'twitter')
    
    def __register(self, funct, args, callback):
        self.queue.put((funct, args, callback))
        
    def quit(self):
        self.exit = True
        
    def run(self):
        while not self.exit:
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
        
    def login(self):
        self.__register(self.core.login, self.account, None)
        
    def get_public(self, callback):
        self.__register(self.core.get_public_timeline, self.account, callback)
    
if __name__ == "__main__":
    turpial = Main()
    turpial.main_loop()


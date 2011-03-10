# -*- coding: utf-8 -*-

"""Widgets para la ventana de preferencias del Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 24, 2009

import gtk
import subprocess

from turpial.api.servicesapi import URL_SERVICES, PHOTO_SERVICES

class Preferences(gtk.Window):
    """Ventana de preferencias de Turpial"""
    def __init__(self, parent=None, mode='user'):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.mode = mode
        self.mainwin = parent
        if self.mode == 'user':
            self.current = parent.read_config()
        self.global_cfg = parent.read_global_config()
        self.set_default_size(360, 380)
        self.set_title(_('Preferences'))
        self.set_border_width(6)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        btn_save = gtk.Button(_('Save'))
        btn_close = gtk.Button(_('Close'))
        
        box_button = gtk.HButtonBox()
        box_button.set_spacing(6)
        box_button.set_layout(gtk.BUTTONBOX_END)
        box_button.pack_start(btn_save)
        box_button.pack_start(btn_close)
        
        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_border_width(3)
        notebook.set_properties('tab-pos', gtk.POS_LEFT)
        
        # Tabs
        if self.mode == 'user':
            self.general = GeneralTab(self.current['General'])
            self.notif = NotificationsTab(self.current['Notifications'])
            self.services = ServicesTab(self.current['Services'])
            self.muted = MutedTab(self.mainwin)
            self.browser = BrowserTab(self.mainwin, self.current['Browser'])
            
            notebook.append_page(self.general, gtk.Label(_('General')))
            notebook.append_page(self.notif, gtk.Label(_('Notifications')))
            notebook.append_page(self.services, gtk.Label(_('Services')))
            notebook.append_page(self.muted, gtk.Label(_('Mute')))
            notebook.append_page(self.browser, gtk.Label(_('Web Browser')))
            
        self.proxy = ProxyTab(self.global_cfg['Proxy'])
        notebook.append_page(self.proxy, gtk.Label(_('API Proxy')))
        
        vbox = gtk.VBox()
        #vbox.set_spacing(4)
        vbox.pack_start(notebook, True, True)
        vbox.pack_start(box_button, False, False)
        
        btn_close.connect('clicked', self.__close)
        btn_save.connect('clicked', self.__save)
        self.connect('delete-event', self.__close)
        
        self.add(vbox)
        self.show_all()
        
    def __close(self, widget, event=None):
        self.destroy()
        
    def __save(self, widget):
        if self.mode == 'user':
            general = self.general.get_config()
            notif = self.notif.get_config()
            services = self.services.get_config()
            browser = self.browser.get_config()
            
            new_config = {
                'General': general,
                'Notifications': notif,
                'Services': services,
                'Browser': browser,
            }
            
            self.mainwin.save_config(new_config)
            self.mainwin.request_mute(self.muted.get_muted())
        
        proxy = self.proxy.get_config()
        new_global = {
            'Proxy': proxy,
        }
        
        self.destroy()
        
        self.mainwin.save_global_config(new_global)
        
class PreferencesTab(gtk.VBox):
    def __init__(self, desc, current=None):
        gtk.VBox.__init__(self, False)
        
        self.current = current
        description = gtk.Label()
        description.set_line_wrap(True)
        description.set_use_markup(True)
        description.set_markup(desc)
        description.set_justify(gtk.JUSTIFY_FILL)
        #desc_box = gtk.HBox(False, 3)
        #desc_box.pack_start(description, True, True)
        
        desc_align = gtk.Alignment(xalign=0.0, yalign=0.0)
        desc_align.set_padding(0, 5, 10, 10)
        desc_align.add(description)
        
        self.pack_start(desc_align, False, False, 5)
        
    def get_config(self):
        raise NotImplemented
        
class TimeScroll(gtk.HBox):
    def __init__(self, label='', val=5, min=1, max=60, step=3, page=6, size=0,
        callback=None, lbl_size=120, unit='min'):
        gtk.HBox.__init__(self, False)
        
        self.callback = callback
        self.value = val
        self.unit = unit
        lbl = gtk.Label(label)
        lbl.set_size_request(lbl_size, -1)
        lbl.set_justify(gtk.JUSTIFY_LEFT)
        adj = gtk.Adjustment(val, min, max, step, page, size)
        scale = gtk.HScale()
        scale.set_digits(0)
        scale.set_adjustment(adj)
        scale.set_property('value-pos', gtk.POS_RIGHT)
        
        self.pack_start(lbl, False, True, 3)
        self.pack_start(scale, True, True, 3)
        
        self.show_all()
        
        scale.connect('format-value', self.__format_value)
        scale.connect('value-changed', self.__on_change)
        
    def __format_value(self, widget, value):
        return "%i %s" % (int(value), self.unit)
        
    def __on_change(self, widget):
        self.value = widget.get_value()
        if self.callback:
            self.callback()
        
class GeneralTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(self, _('Adjust update frequency for \
timeline, mentions and direct messages'), current)
        
        h = int(self.current['home-update-interval'])
        r = int(self.current['replies-update-interval'])
        d = int(self.current['directs-update-interval'])
        t = int(self.current['num-tweets'])
        pf = True if self.current['profile-color'] == 'on' else False
        ws = True if self.current['workspace'] == 'wide' else False
        min = True if self.current['minimize-on-close'] == 'on' else False
        
        self.home = TimeScroll(_('Column 1 (Left)'), h,
            callback=self.update_api_calls)
        self.replies = TimeScroll(_('Column 2 (Middle)'), r,
            callback=self.update_api_calls)
        self.directs = TimeScroll(_('Column 3 (Right)'), d, 
            callback=self.update_api_calls)
        
        self.tweets = TimeScroll(_('Tweets shown'), t, min=20, max=200,
            unit='', lbl_size=120)
        
        self.estimated = gtk.Label(_('You will use 0 calls to API per hour'))
        est_align = gtk.Alignment(xalign=0.5)
        est_align.set_padding(0, 8, 0, 0)
        est_align.add(self.estimated)
        
        self.workspace = gtk.CheckButton(_('Wide Mode'))
        self.workspace.set_active(ws)
        try:
            self.workspace.set_has_tooltip(True)
            self.workspace.set_tooltip_text(_('Show a workspace of 3 columns'))
        except:
            pass
        
        self.profile_colors = gtk.CheckButton(_('Load profile color \
(Needs restart Turpial)'))
        self.profile_colors.set_active(pf)
        try:
            self.profile_colors.set_has_tooltip(True)
            self.profile_colors.set_tooltip_text(_('Use user profile color \
to highlight mentions, hashtags and URLs'))
        except:
            pass
        
        self.minimize = gtk.CheckButton(_('Minimize to tray'))
        self.minimize.set_active(min)
        try:
            self.minimize.set_has_tooltip(True)
            self.minimize.set_tooltip_text(_('Send Turpial to system tray \
when close'))
        except:
            pass
        
        self.pack_start(self.home, False, False, 5)
        self.pack_start(self.replies, False, False, 5)
        self.pack_start(self.directs, False, False, 5)
        self.pack_start(est_align, False, False, 4)
        self.pack_start(self.tweets, False, False, 10)
        self.pack_start(self.workspace, False, False, 2)
        self.pack_start(self.profile_colors, False, False, 2)
        self.pack_start(self.minimize, False, False, 2)
        self.show_all()
        self.update_api_calls()
        
    def update_api_calls(self):
        calls = (60 / self.home.value) + (60 / self.replies.value) + \
            (60 / self.directs.value)
        self.estimated.set_text(_('You will use aprox. %i calls to API per \
hour') % calls)
        
    def get_config(self):
        ws = 'wide' if self.workspace.get_active() else 'single'
        min = 'on' if self.minimize.get_active() else 'off'
        pf = 'on' if self.profile_colors.get_active() else 'off'
        
        return {
            'home-update-interval': int(self.home.value),
            'replies-update-interval': int(self.replies.value),
            'directs-update-interval': int(self.directs.value),
            'workspace': ws,
            'profile-color': pf,
            'minimize-on-close': min,
            'num-tweets': int(self.tweets.value),
        }

class NotificationsTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(self, _('Select what notifications you want \
to receive from Turpial'), current)
        
        home = True if self.current['home'] == 'on' else False
        replies = True if self.current['replies'] == 'on' else False
        directs = True if self.current['directs'] == 'on' else False
        login = True if self.current['login'] == 'on' else False
        sound = True if self.current['sound'] == 'on' else False
        
        self.timeline = gtk.CheckButton(_('Column 1 (Left)'))
        self.timeline.set_active(home)
        try:
            self.timeline.set_has_tooltip(True)
            '''
            self.timeline.set_tooltip_text(_('Show a notification when \
            Timeline is updated'))
            '''
        except:
            pass
            
        self.replies = gtk.CheckButton(_('Column 2 (Middle)'))
        self.replies.set_active(replies)
        try:
            self.replies.set_has_tooltip(True)
            '''
            self.replies.set_tooltip_text(_('Show a notification when you \
            get mentions from other users'))
            '''
        except:
            pass
            
        self.directs = gtk.CheckButton(_('Column 3 (Right)'))
        self.directs.set_active(directs)
        try:
            self.directs.set_has_tooltip(True)
            '''
            self.directs.set_tooltip_text(_('Show a notification when you \
            get direct messages'))
            '''
        except:
            pass
            
        self.profile = gtk.CheckButton(_('Login'))
        self.profile.set_active(login)
        try:
            self.profile.set_has_tooltip(True)
            self.profile.set_tooltip_text(_('Show a notification at login \
with your user info'))
        except:
            pass
        
        self.sounds = gtk.CheckButton(_('Activate sounds'))
        self.sounds.set_active(sound)
        try:
            self.sounds.set_has_tooltip(True)
            self.sounds.set_tooltip_text(_('Activate sounds for each \
notification'))
        except:
            pass
            
        self.pack_start(self.timeline, False, False, 2)
        self.pack_start(self.replies, False, False, 2)
        self.pack_start(self.directs, False, False, 2)
        self.pack_start(self.profile, False, False, 2)
        self.pack_start(self.sounds, False, False, 6)
        self.show_all()
        
    def get_config(self):
        home = 'on' if self.timeline.get_active() else 'off'
        replies = 'on' if self.replies.get_active() else 'off'
        directs = 'on' if self.directs.get_active() else 'off'
        profile = 'on' if self.profile.get_active() else 'off'
        sound = 'on' if self.sounds.get_active() else 'off'
        
        return {
            'home': home,
            'replies': replies,
            'directs': directs,
            'login': profile,
            'sound': sound,
        }
        
class ServicesTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(self, _('Select your preferred services for \
shorten URLs and upload images'), current)
        i = 0
        default = -1
        lbl_size = 120
        
        url_lbl = gtk.Label(_('Shorten URL'))
        url_lbl.set_size_request(lbl_size, -1)
        self.shorten = gtk.combo_box_new_text()
        for key, v in URL_SERVICES.iteritems():
            self.shorten.append_text(key)
            if key == self.current['shorten-url']:
                default = i
            i += 1
        self.shorten.set_active(default)
        
        url_box = gtk.HBox(False)
        url_box.pack_start(url_lbl, False, False, 3)
        url_box.pack_start(self.shorten, False, False, 3)
        
        pic_lbl = gtk.Label(_('Upload images'))
        pic_lbl.set_size_request(lbl_size, -1)
        self.upload = gtk.combo_box_new_text()
        i = 0
        for key in PHOTO_SERVICES:
            self.upload.append_text(key)
            if key == self.current['upload-pic']:
                default = i
            i += 1
        self.upload.set_active(default)
        
        pic_box = gtk.HBox(False)
        pic_box.pack_start(pic_lbl, False, False, 3)
        pic_box.pack_start(self.upload, False, False, 3)
        
        self.pack_start(url_box, False, False, 2)
        self.pack_start(pic_box, False, False, 2)
        self.show_all()
        
    def get_config(self):
        return {
            'shorten-url': self.shorten.get_active_text(),
            'upload-pic': self.upload.get_active_text(),
        }
        
class MutedTab(PreferencesTab):
    def __init__(self, parent):
        PreferencesTab.__init__(self, _('Select all those users that are \
bothering you and shut them up temporarily'))
        
        self.muted = []
        self.mainwin = parent
        self.muted = self.mainwin.request_muted_list()
        self.friends = self.mainwin.request_friends_list()
        
        self.model = gtk.ListStore(str, bool)
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.list.set_model(self.model)
        
        cell_check = gtk.CellRendererToggle()
        cell_check.set_property('activatable', True)
        cell_user = gtk.CellRendererText()
        
        column = gtk.TreeViewColumn('')
        column.set_alignment(0.0)
        column.pack_start(cell_check, False)
        column.pack_start(cell_user, True)
        column.set_attributes(cell_check, active=1)
        column.set_attributes(cell_user, markup=0)
        self.list.append_column(column)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.list)
        
        cell_check.connect("toggled", self.__toggled)
        
        label = gtk.Label()
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.set_justify(gtk.JUSTIFY_FILL)
        
        align = gtk.Alignment(xalign=0.0, yalign=0.0)
        align.set_padding(0, 5, 10, 10)
        align.add(label)
        
        if self.friends is not None:
            if len(self.friends) > 0:
                for f in self.friends:
                    mark = True if (f in self.muted) else False
                    self.model.append([f, mark])
                    
                self.pack_start(scroll, True, True, 2)
            elif len(self.friends) == 0:
                label.set_markup('<span foreground="#920d12">%s</span>' % 
                _('What? You don\'t have any friends. Try to go out and know \
some nice people' ))
                self.pack_start(align, True, True, 2)
        else:
            label.set_markup('<span foreground="#920d12">%s</span>' % 
            _('I am still loading all of your friends. Try again in a few \
seconds' ))
            self.pack_start(align, True, True, 2)
        
        self.show_all()
        
    def __process(self, model, path, iter):
        user = model.get_value(iter, 0)
        mark = model.get_value(iter, 1)
        
        if mark:
            self.muted.append(user)
            
    def __toggled(self, widget, path):
        value = not self.model[path][1]
        self.model[path][1] = value
        
    def get_muted(self):
        self.muted = []
        self.model.foreach(self.__process)
        return self.muted

class BrowserTab(PreferencesTab):
    def __init__(self, parent, current):
        PreferencesTab.__init__(self, _('Setup your favorite web browser to \
open all links'), current)
        
        self.mainwin = parent
        
        chk_default = gtk.RadioButton(None,
            _('Default web browser'))
        chk_other = gtk.RadioButton(chk_default,
            _('Choose another web browser'))
        
        cmd_lbl = gtk.Label(_('Command'))
        self.command = gtk.Entry()
        btn_test = gtk.Button(_('Test'))
        btn_browse = gtk.Button(_('Browse'))
        
        cmd_box = gtk.HBox(False)
        cmd_box.pack_start(cmd_lbl, False, False, 3)
        cmd_box.pack_start(self.command, True, True, 3)
        
        buttons_box = gtk.HButtonBox()
        buttons_box.set_spacing(6)
        buttons_box.set_layout(gtk.BUTTONBOX_END)
        buttons_box.pack_start(btn_test)
        buttons_box.pack_start(btn_browse)
        
        self.other_vbox = gtk.VBox(False, 2)
        self.other_vbox.pack_start(cmd_box, False, False, 2)
        self.other_vbox.pack_start(buttons_box, False, False, 2)
        self.other_vbox.set_sensitive(False)
        
        self.pack_start(chk_default, False, False, 2)
        self.pack_start(chk_other, False, False, 2)
        self.pack_start(self.other_vbox, False, False, 2)
        
        if current['cmd'] != '':
            self.other_vbox.set_sensitive(True)
            self.command.set_text(current['cmd'])
            chk_other.set_active(True)
        
        btn_browse.connect('clicked', self.__browse)
        btn_test.connect('clicked', self.__test)
        chk_default.connect('toggled', self.__activate, 'default')
        chk_other.connect('toggled', self.__activate, 'other')
        
        self.show_all()
        
    def __test(self, widget):
        cmd = self.command.get_text()
        if cmd != '':
            subprocess.Popen([cmd, 'http://turpial.org.ve/'])
            
    def __browse(self, widget):
        dia = gtk.FileChooserDialog(title=_('Select the full path of your \
web browser'),
            parent=self.mainwin,
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OK, gtk.RESPONSE_OK))
        resp = dia.run()
        
        if resp == gtk.RESPONSE_OK:
            self.command.set_text(dia.get_filename())
        dia.destroy()
        
    def __activate(self, widget, param):
        if param == 'default':
            self.other_vbox.set_sensitive(False)
            self.command.set_text('')
        else:
            self.other_vbox.set_sensitive(True)
            
    def get_config(self):
        return {
            'cmd': self.command.get_text()
        }
        
class ProxyTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(self, _('Proxy settings for Turpial (Need \
Restart)'), current)
        
        chk_none = gtk.RadioButton(None, _('No proxy'))
        chk_url = gtk.RadioButton(chk_none, _('Twitter API proxy'))
        
        try:
            chk_url.set_has_tooltip(True)
            chk_url.set_tooltip_text(_('Use a URL to access Twitter API \
different of twitter.com'))
        except:
            pass
        url_lbl = gtk.Label(_('Twitter API URL'))
        self.url = gtk.Entry()
        
        self.url_box = gtk.HBox(False)
        self.url_box.pack_start(url_lbl, False, False, 3)
        self.url_box.pack_start(self.url, True, True, 3)
        self.url_box.set_sensitive(False)
        
        self.pack_start(chk_none, False, False, 2)
        self.pack_start(chk_url, False, False, 2)
        self.pack_start(self.url_box, False, False, 2)
        
        if current['url'] != '':
            self.url_box.set_sensitive(True)
            self.url.set_text(current['url'])
            chk_url.set_active(True)
        else:
            chk_none.set_active(True)
        
        chk_none.connect('toggled', self.__activate, 'none')
        chk_url.connect('toggled', self.__activate, 'url')
        
        self.show_all()
        
    def __activate(self, widget, param):
        if param == 'none':
            self.url_box.set_sensitive(False)
            self.url.set_text('')
        elif param == 'url':
            self.url_box.set_sensitive(True)
            
    def get_config(self):
        return {
            'username': '',
            'password': '',
            'server': '',
            'port': '',
            'url': self.url.get_text()
        }
        

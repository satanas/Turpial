# -*- coding: utf-8 -*-

""" Preferences dialog for Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# March 2, 2012

import gtk
import subprocess

from libturpial.api.services.uploadpic.servicelist import PIC_SERVICES
from libturpial.api.services.shorturl.servicelist import URL_SERVICES

class Preferences(gtk.Window):
    def __init__(self, parent=None, mode='user'):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.mainwin = parent
        self.current = parent.get_config()
        self.set_default_size(450, 400)
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
        box_button.pack_start(btn_close)
        box_button.pack_start(btn_save)

        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_border_width(3)
        notebook.set_properties('tab-pos', gtk.POS_LEFT)

        # Tabs
        self.general = GeneralTab(self.current['General'])
        self.notif = NotificationsTab(self.current['Notifications'],
            self.current['Sounds'])
        self.services = ServicesTab(self.current['Services'])
        self.browser = BrowserTab(self.mainwin, self.current['Browser'])
        self.filtered = FilterTab(self.mainwin)
        #self.advanced = AdvancedTab(self.mainwin, self.current['Advanced'])

        notebook.append_page(self.general, gtk.Label(_('General')))
        notebook.append_page(self.notif, gtk.Label(_('Notifications')))
        notebook.append_page(self.services, gtk.Label(_('Services')))
        notebook.append_page(self.browser, gtk.Label(_('Web Browser')))
        notebook.append_page(self.filtered, gtk.Label(_('Filters')))
        #notebook.append_page(self.advanced, gtk.Label(_('Advanced')))

        ##self.proxy = ProxyTab(self.global_cfg['Proxy'])
        ##notebook.append_page(self.proxy, gtk.Label(_('API Proxy')))

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
        general = self.general.get_config()
        notif, sounds = self.notif.get_config()
        services = self.services.get_config()
        browser = self.browser.get_config()
        advanced = self.browser.get_config()

        new_config = {
            'General': general,
            'Notifications': notif,
            'Sounds': sounds,
            'Services': services,
            'Browser': browser,
            'Advanced': advanced,
        }

        '''
        self.mainwin.request_mute(self.muted.get_muted())
        self.mainwin.request_filter(self.filtered.get_filtered())
        '''
        print new_config
        self.destroy()

        self.mainwin.save_config(new_config)

class PreferencesTab(gtk.VBox):
    def __init__(self, desc, current=None):
        gtk.VBox.__init__(self, False)

        self.current = current
        description = gtk.Label()
        description.set_line_wrap(True)
        description.set_use_markup(True)
        description.set_markup(desc)
        description.set_justify(gtk.JUSTIFY_FILL)

        desc_align = gtk.Alignment(xalign=0.0, yalign=0.0)
        desc_align.set_padding(0, 5, 10, 10)
        desc_align.add(description)

        self.container = gtk.VBox(False, 2)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(self.container, True, True, 10)

        self.pack_start(desc_align, False, False, 5)
        self.pack_start(hbox, True, True)

    def add_child(self, child, expand=True, fill=True, padding=0):
        self.container.pack_start(child, expand, fill, padding)

    def get_config(self):
        raise NotImplemented

class TitleLabel(gtk.Alignment):
    def __init__(self, text, padding=0):
        gtk.Alignment.__init__(self, xalign=0.0, yalign=0.0)
        caption ="<big><b>%s</b></big>" % text
        label = gtk.Label()
        label.set_line_wrap(True)
        label.set_use_markup(True)
        label.set_markup(caption)
        label.set_justify(gtk.JUSTIFY_FILL)

        self.set_padding(10, 0, padding, 0)
        self.add(label)

class CheckBox(gtk.Alignment):
    def __init__(self, title, is_active, tooltip, padding=0):
        gtk.Alignment.__init__(self)
        self.set_padding(0, 0, padding, 0)

        self.checkbtn = gtk.CheckButton(title)
        self.checkbtn.set_active(is_active)
        try:
            self.checkbtn.set_has_tooltip(True)
            self.checkbtn.set_tooltip_text(tooltip)
        except Exception:
            pass
        self.add(self.checkbtn)

    def get_active(self):
        return self.checkbtn.get_active()

class HSeparator(gtk.HBox):
    def __init__(self, spacing=15):
        gtk.HBox.__init__(self, False)
        self.set_size_request(-1, spacing)

class TimeScroll(gtk.HBox):
    def __init__(self, caption='', val=5, min=1, max=60, step=3, page=6, size=0,
        lbl_size=150, unit=''):
        gtk.HBox.__init__(self, False)

        self.value = val
        self.unit = unit
        self.caption = caption

        self.label = gtk.Label()
        self.label.set_size_request(lbl_size, -1)
        self.label.set_alignment(xalign=0.0, yalign=0.5)
        self.label.set_use_markup(True)

        adj = gtk.Adjustment(val, min, max, step, page, size)
        scale = gtk.HScale()
        scale.set_draw_value(False)
        scale.set_adjustment(adj)
        scale.set_property('value-pos', gtk.POS_RIGHT)

        self.pack_start(scale, True, True, 3)
        self.pack_start(self.label, False, False, 3)

        self.show_all()
        self.__on_change(scale)
        scale.connect('value-changed', self.__on_change)

    def __on_change(self, widget):
        value = widget.get_value()
        label = "%s <span foreground='#999999'>%i %s</span>" % (self.caption,
            value, self.unit)
        self.label.set_markup(label)

class GeneralTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(
            self,
            _('Adjust update frequency for columns'),
            current
        )

        interval = int(self.current['update-interval'])
        tweets = int(self.current['num-tweets'])
        profile = True if self.current['profile-color'] == 'on' else False
        minimize = True if self.current['minimize-on-close'] == 'on' else False

        self.interval = TimeScroll(_('Update Interval'), interval, unit='min')
        self.tweets = TimeScroll(_('Statuses'), tweets, min=20, max=200)

        self.profile_colors = CheckBox(_('Load profile color'), profile,
            _('Use your profile color for highlighted elements'))

        self.minimize = CheckBox(_('Minimize to tray'), minimize,
            _('Send Turpial to system tray when closing main window'))

        self.add_child(self.interval, False, False, 5)
        self.add_child(self.tweets, False, False, 5)
        self.add_child(HSeparator(), False, False)
        self.add_child(self.profile_colors, False, False, 2)
        self.add_child(self.minimize, False, False, 2)
        self.show_all()

    def get_config(self):
        minimize = 'on' if self.minimize.get_active() else 'off'
        profile = 'on' if self.profile_colors.get_active() else 'off'

        return {
            'update-interval': int(self.interval.value),
            'profile-color': profile,
            'minimize-on-close': minimize,
            'num-tweets': int(self.tweets.value),
        }

class NotificationsTab(PreferencesTab):
    def __init__(self, notif, sounds):
        PreferencesTab.__init__(
            self,
            _('Select the notifications you want to receive from Turpial'),
            None
        )
        self.notif = notif
        self.sounds = sounds

        nupdates  = True if self.notif['updates'] == 'on' else False
        nlogin = True if self.notif['login'] == 'on' else False
        nicon = True if self.notif['icon'] == 'on' else False
        slogin = True if self.sounds['login'] == 'on' else False
        supdates = True if self.sounds['updates'] == 'on' else False

        self.nupdates = CheckBox(_('Updates'), nupdates,
            _('Show a notification when you get updates'), 10)

        self.nlogin = CheckBox(_('Login'), nlogin,
            _('Show a notification at login with user profile'), 10)

        self.nicon = CheckBox(_('Tray icon'), nicon, 
            _('Change the tray icon when you have notifications'), 10)

        self.slogin = CheckBox(_('Login'), slogin,
            _('Play a sound when you login'), 10)

        self.supdates = CheckBox(_('Updates'), supdates,
            _('Play a sound when you get updates'), 10)

        self.add_child(TitleLabel(_('Notifications')), False, False)
        self.add_child(self.nlogin, False, False, 2)
        self.add_child(self.nupdates, False, False, 2)
        self.add_child(self.nicon, False, False, 2)
        self.add_child(TitleLabel(_('Sounds')), False, False)
        self.add_child(self.slogin, False, False, 2)
        self.add_child(self.supdates, False, False, 2)
        self.show_all()

    def get_config(self):
        nupdates = 'on' if self.nupdates.get_active() else 'off'
        nlogin = 'on' if self.nlogin.get_active() else 'off'
        nicon = 'on' if self.nicon.get_active() else 'off'
        slogin = 'on' if self.slogin.get_active() else 'off'
        supdates = 'on' if self.supdates.get_active() else 'off'

        return {
            'updates': nupdates,
            'login': nlogin,
            'icon': nicon,
        }, {
            'login': slogin,
            'updates': supdates,
        }

class ServicesTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(
            self,
            _('Select your preferred services '
              'to shorten URLs and to upload images'),
            current
        )
        i = 0
        default = -1
        lbl_size = 120

        url_lbl = gtk.Label(_('Shorten URL'))
        url_lbl.set_size_request(lbl_size, -1)
        url_lbl.set_alignment(1.0, 0.5)
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
        pic_lbl.set_alignment(1.0, 0.5)
        self.upload = gtk.combo_box_new_text()
        i = 0
        for key, v in PIC_SERVICES.iteritems():
            self.upload.append_text(key)
            if key == self.current['upload-pic']:
                default = i
            i += 1
        self.upload.set_active(default)

        pic_box = gtk.HBox(False)
        pic_box.pack_start(pic_lbl, False, False, 3)
        pic_box.pack_start(self.upload, False, False, 3)

        self.add_child(url_box, False, False, 2)
        self.add_child(pic_box, False, False, 2)
        self.show_all()

    def get_config(self):
        return {
            'shorten-url': self.shorten.get_active_text(),
            'upload-pic': self.upload.get_active_text(),
        }

class FilterTab(PreferencesTab):
    def __init__(self, parent):
        PreferencesTab.__init__(
            self, 
            _("Filter out words you don't want to see")
        )

        self.mainwin = parent

        self.filtered = self.mainwin.get_filters()
        self.updated_filtered = set(self.filtered)
        input_box = gtk.HBox()
        input_box.pack_start(gtk.Label(_("New Filter")), False, False, 0)
        self.term_input = gtk.Entry()
        input_box.pack_start(self.term_input, True, True, 2)
        add_button = gtk.Button(stock=gtk.STOCK_ADD)
        add_button.connect("clicked", self._add_filter, "add_filter_button")
        input_box.pack_start(add_button, False, False, 0)
        remove_button = gtk.Button(stock=gtk.STOCK_DELETE)
        remove_button.connect("clicked", self._remove_filter, "remove_filter_button")
        input_box.pack_start(remove_button, False, False, 0)

        self.model = gtk.ListStore(str)
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        self.list.set_model(self.model)

        column = gtk.TreeViewColumn('')
        column.set_alignment(0.0)
        cell_term = gtk.CellRendererText()
        column.pack_start(cell_term, True)
        column.set_attributes(cell_term, markup=0)
        self.list.append_column(column)

        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.list)

        for filtered_item in self.filtered:
            self.model.append([filtered_item])

        self.add_child(input_box, False, False, 2)
        self.add_child(scroll, True, True, 2)
        self.show_all()

    def __process(self, model, path, iter):
        filtered_item = model.get_value(iter, 0)
        self.filtered.append(filtered_item)

    def get_filtered(self):
        self.filtered = []
        self.model.foreach(self.__process)
        return self.filtered

    def _add_filter(self, widget, data=None):
        new_filter_term = self.term_input.get_text()
        if new_filter_term and new_filter_term not in self.updated_filtered:
            self.model.append([new_filter_term])
            self.updated_filtered.add(new_filter_term)
        self.term_input.set_text("")

    def _remove_filter(self, widget, data=None):
        model, term = self.list.get_selection().get_selected()
        if term:
            str_term = self.model.get_value(term, 0)
            self.model.remove(term)
            self.updated_filtered.remove(str_term)

class BrowserTab(PreferencesTab):
    def __init__(self, parent, current):
        PreferencesTab.__init__(
            self,
            _('Setup your favorite web browser to open all links'),
            current
        )

        self.mainwin = parent

        chk_default = gtk.RadioButton(None,
            _('Default web browser'))
        chk_other = gtk.RadioButton(chk_default,
            _('Choose another web browser'))

        cmd_lbl = gtk.Label(_('Command'))
        cmd_lbl.set_size_request(90, -1)
        cmd_lbl.set_alignment(1.0, 0.5)
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

        self.add_child(chk_default, False, False, 2)
        self.add_child(chk_other, False, False, 2)
        self.add_child(self.other_vbox, False, False, 2)

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
        dia = gtk.FileChooserDialog(
            title = _('Select the full path of your web browser'),
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

class AdvancedTab(PreferencesTab):
    def __init__(self, mainwin, current):
        PreferencesTab.__init__(
            self,
            _('Advanced options. Use it only if you know what you do'),
            current
        )

        self.mainwin = mainwin
        cachelbl = gtk.Label(_('Clean images cache'))
        cachebtn = gtk.Button(_('Clean'))
        cachebtn.connect('clicked', self.__clean_cache)

        configlbl = gtk.Label(_('Restore default config'))
        configbtn = gtk.Button(_('Restore'))
        configbtn.connect('clicked', self.__restore_default_config)

        table = gtk.Table(2, 2, True)
        #table.attach(cachelbl, 0, 1, 0, 1, gtk.EXPAND|gtk.FILL)
        #table.attach(cachebtn, 1, 2, 0, 1, gtk.EXPAND|gtk.FILL)
        #table.attach(configlbl, 0, 1, 1, 2, gtk.EXPAND|gtk.FILL)
        #table.attach(configbtn, 1, 2, 1, 2, gtk.EXPAND|gtk.FILL)
        table.attach(cachebtn, 0, 1, 0, 1)
        table.attach(configbtn, 0, 1, 1, 2)

        timeout = int(self.current['socket-timeout'])
        show_avatars = True if self.current['show-user-avatars'] == 'on' else False

        self.timeout = TimeScroll(_('Connection Timeout'), timeout, min=5, max=120,
            unit=_('seconds'), lbl_size=120)

        self.show_avatars = gtk.CheckButton(_('Load user avatars in columns'))
        self.show_avatars.set_active(show_avatars)
        try:
            self.show_avatars.set_has_tooltip(True)
            self.show_avatars.set_tooltip_text(_(
                'Disable loading user avatars for slow connections'))
        except:
            pass

        self.add_child(table, False, False, 2)
        self.add_child(self.timeout, False, False, 2)
        self.add_child(self.show_avatars, False, False, 2)
        self.show_all()

    def __clean_cache(self, widget):
        pass

    def __restore_default_config(self, widget):
        pass

    def get_config(self):
        show_avatars = 'on' if self.show_avatars.get_active() else 'off'

        return {
            'socket-timeout': int(self.timeout.value),
            'show-user-avatars': show_avatars,
        }

class ProxyTab(PreferencesTab):
    def __init__(self, current):
        PreferencesTab.__init__(
            self,
            _('Proxy settings for Turpial (Need Restart)'),
            current
        )

        chk_none = gtk.RadioButton(None, _('No proxy'))
        chk_url = gtk.RadioButton(chk_none, _('Proxy'))

        try:
            chk_url.set_has_tooltip(True)
            chk_url.set_tooltip_text(
                _('Use a proxy to access internet'))
        except:
            pass
        url_lbl = gtk.Label(_('Twitter API URL'))
        self.url = gtk.Entry()

        self.url_box = gtk.HBox(False)
        self.url_box.pack_start(url_lbl, False, False, 3)
        self.url_box.pack_start(self.url, True, True, 3)
        self.url_box.set_sensitive(False)

        self.add_child(chk_none, False, False, 2)
        self.add_child(chk_url, False, False, 2)
        self.add_child(self.url_box, False, False, 2)

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
